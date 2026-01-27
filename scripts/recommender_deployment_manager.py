"""
Recommender Model Deployment Manager
Handles versioning, backup, testing, and rollback for ADS Recommender deployments.
"""

import os
import re
import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import ads
from ads.model.deployment import ModelDeployment
from ads.model import GenericModel

try:
    import oci
    from oci.data_science import DataScienceClient
    from oci.data_science.models import (
        UpdateModelDeploymentDetails,
        UpdateSingleModelDeploymentConfigurationDetails,
        UpdateModelConfigurationDetails,
    )
    _OCI_AVAILABLE = True
except ImportError:
    _OCI_AVAILABLE = False


class RecommenderDeploymentManager:
    """Manages versioning and deployment of recommender models."""
    
    def __init__(
        self,
        project_name: str = "Product Recommender",
        backup_root: str = "/home/datascience/backups",
        artifact_dir: str = "/home/datascience/recommender_model_artifact",
        results_dir: str = "/home/datascience/results"
    ):
        self.project_name = project_name
        self.backup_root = Path(backup_root)
        self.artifact_dir = Path(artifact_dir)
        self.results_dir = Path(results_dir)
        
        # Ensure backup directory exists
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # State file to track deployments
        self.state_file = self.backup_root / "deployment_state.json"
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load deployment state from file."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "current_version": 0,
            "production_deployment": None,
            "test_deployment": None,
            "deployment_history": []
        }
    
    def _save_state(self):
        """Save deployment state to file."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _get_ds_client(self, deployment_id: str):
        """Build OCI DataScienceClient. Region parsed from deployment_id."""
        if not _OCI_AVAILABLE:
            raise RuntimeError("oci package is required for OCI client update/verify; install oci.")
        m = re.search(r"\.oc1\.([^.]+)\.", deployment_id)
        region = m.group(1) if m else os.environ.get("NB_REGION", "ap-singapore-1")
        signer = ads.common.auth.default_signer()
        return DataScienceClient({"region": region}, signer=signer)
    
    def _verify_deployment_model(self, deployment_id: str, expected_model_id: str) -> None:
        """Verify the deployment's model_id in OCI. Raises if mismatch or unable to determine."""
        client = self._get_ds_client(deployment_id)
        r = client.get_model_deployment(deployment_id)
        mdc = getattr(r.data, "model_deployment_configuration_details", None)
        mcd = getattr(mdc, "model_configuration_details", None) if mdc else None
        actual = getattr(mcd, "model_id", None) if mcd else None
        if actual != expected_model_id:
            raise RuntimeError(
                f"Update did not apply: deployment model is {actual}, expected {expected_model_id}. "
                "Production was NOT changed. Test deployment was NOT deleted."
            )
    
    def _update_deployment_model_oci(self, deployment_id: str, model_id: str) -> None:
        """Update deployment's model via OCI client (bypasses ADS when it 400s or ignores)."""
        if not _OCI_AVAILABLE:
            raise RuntimeError("oci package is required for OCI client update.")
        client = self._get_ds_client(deployment_id)
        mcd = UpdateModelConfigurationDetails(model_id=model_id)
        mdc = UpdateSingleModelDeploymentConfigurationDetails(model_configuration_details=mcd)
        details = UpdateModelDeploymentDetails(model_deployment_configuration_details=mdc)
        client.update_model_deployment(deployment_id, details)
        # OCI update is async (202); wait before verify
        print("   Waiting for OCI update to apply (90s)...")
        time.sleep(90)
    
    def get_next_version(self) -> int:
        """Get the next version number."""
        return self.state["current_version"] + 1
    
    def backup_current_artifacts(self, version: Optional[int] = None) -> Path:
        """
        Backup current model artifacts and results.
        
        Args:
            version: Version number for the backup. If None, uses timestamp.
        
        Returns:
            Path to backup directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if version:
            backup_name = f"v{version}_{timestamp}"
        else:
            backup_name = f"backup_{timestamp}"
        
        backup_dir = self.backup_root / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📦 Creating backup: {backup_dir}")
        
        # Backup results folder
        if self.results_dir.exists():
            backup_results = backup_dir / "results"
            shutil.copytree(self.results_dir, backup_results)
            print(f"  ✓ Backed up results")
        
        # Backup model artifacts
        if self.artifact_dir.exists():
            backup_artifacts = backup_dir / "recommender_model_artifact"
            shutil.copytree(self.artifact_dir, backup_artifacts)
            print(f"  ✓ Backed up model artifacts")
        
        # Save metadata
        metadata = {
            "version": version,
            "timestamp": timestamp,
            "backup_date": datetime.now().isoformat(),
            "production_deployment": self.state.get("production_deployment"),
            "project_name": self.project_name
        }
        
        with open(backup_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"  ✓ Backup complete: {backup_dir}\n")
        return backup_dir
    
    def save_new_model(
        self,
        model: GenericModel,
        version: int,
        num_users: int,
        num_products: int,
        is_test: bool = True
    ) -> str:
        """
        Save a new model to the Model Catalog.
        
        Args:
            model: The GenericModel instance to save
            version: Version number
            num_users: Number of users in training data
            num_products: Number of products
            is_test: Whether this is a test deployment (default: True)
        
        Returns:
            Model OCID
        """
        status = "TEST" if is_test else "PRODUCTION"
        display_name = f"{self.project_name} v{version} ({status})"
        description = f"Trained with {num_users:,} users and {num_products:,} products"
        
        if is_test:
            description += " - TESTING"
        
        print(f"💾 Saving model: {display_name}")
        
        model_id = model.save(
            display_name=display_name,
            description=description,
            timeout=600,
            ignore_introspection=True
        )
        
        print(f"  ✓ Model saved! OCID: {model_id}\n")
        return model_id
    
    def deploy_model(
        self,
        model: GenericModel,
        model_id: str,
        version: int,
        is_test: bool = True,
        instance_shape: str = "VM.Standard.E4.Flex",
        ocpus: int = 1,
        memory_gb: int = 16
    ) -> ModelDeployment:
        """
        Deploy a model to an endpoint.
        
        Args:
            model: The GenericModel instance
            model_id: Model OCID
            version: Version number
            is_test: Whether this is a test deployment
            instance_shape: OCI compute shape
            ocpus: Number of OCPUs
            memory_gb: Memory in GB
        
        Returns:
            ModelDeployment instance
        """
        status = "TEST" if is_test else "PRODUCTION"
        display_name = f"{self.project_name} API v{version} ({status})"
        
        print(f"🚀 Deploying model: {display_name}")
        print(f"   Shape: {instance_shape}, OCPUs: {ocpus}, Memory: {memory_gb}GB")
        
        deployment = model.deploy(
            display_name=display_name,
            deployment_instance_shape=instance_shape,
            deployment_ocpus=ocpus,
            deployment_memory_in_gbs=memory_gb,
            wait_for_completion=True
        )
        
        deployment_info = {
            "deployment_id": deployment.model_deployment_id,
            "model_id": model_id,
            "endpoint": deployment.url,
            "version": version,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "shape": instance_shape,
            "ocpus": ocpus,
            "memory_gb": memory_gb
        }
        
        if is_test:
            self.state["test_deployment"] = deployment_info
        else:
            self.state["production_deployment"] = deployment_info
        
        self.state["deployment_history"].append(deployment_info)
        self._save_state()
        
        print(f"  ✓ Deployment complete!")
        print(f"  ✓ Endpoint: {deployment.url}\n")
        
        return deployment
    
    def promote_to_production(self, test_deployment_id: Optional[str] = None):
        """
        Promote test deployment to production by updating the production endpoint.
        
        Args:
            test_deployment_id: Test deployment ID. If None, uses current test deployment.
        """
        test_info = self.state.get("test_deployment")
        prod_info = self.state.get("production_deployment")
        
        if not test_info:
            raise ValueError("No test deployment found. Deploy a test version first.")
        
        if test_deployment_id and test_info["deployment_id"] != test_deployment_id:
            raise ValueError(f"Test deployment ID mismatch: {test_deployment_id}")
        
        print(f"🔄 Promoting v{test_info['version']} to production...")
        
        if prod_info:
            # Update existing production deployment. Prefer OCI client (ADS can 400 or ignore).
            # Always verify; only then delete test and update state. ADS may log 400 without raising.
            print(f"   Updating production deployment: {prod_info['deployment_id']}")
            oci_used = False
            try:
                try:
                    self._update_deployment_model_oci(prod_info["deployment_id"], test_info["model_id"])
                    oci_used = True
                except Exception:
                    prod_deployment = ModelDeployment.from_id(prod_info["deployment_id"])
                    prod_deployment.update(model_id=test_info["model_id"])
                if not oci_used:
                    time.sleep(10)
                self._verify_deployment_model(prod_info["deployment_id"], test_info["model_id"])
            except Exception as e:
                print(f"  ❌ Promote failed: {e}")
                print(f"  Production was NOT changed. Test deployment was NOT deleted.")
                raise RuntimeError(
                    f"Promote failed. Production still on v{self.state.get('current_version', '?')}. "
                    f"Original: {e}"
                ) from e
            
            # Only reached if update and verify succeeded
            endpoint = prod_info["endpoint"]
            print(f"  ✓ Production updated to use model: {test_info['model_id']}")
            print(f"  ✓ Same endpoint URL: {endpoint}")
            try:
                ModelDeployment.from_id(test_info["deployment_id"]).delete(wait_for_completion=True)
                print(f"  ✓ Test deployment deleted")
            except Exception as e:
                print(f"  ⚠️  Could not delete test deployment: {e}")
        else:
            # No production deployment exists, promote test to production
            print(f"   No existing production deployment, promoting test deployment...")
            _ = ModelDeployment.from_id(test_info["deployment_id"])  # ensure it exists
            # Note: OCI doesn't allow updating display name directly,
            # so we just update our state tracking
            endpoint = test_info["endpoint"]
            print(f"  ✓ Test deployment promoted to production")
            print(f"  ✓ Endpoint: {endpoint}")
        
        # Update state (only reached if OCI update succeeded or there was no prod to update)
        now = datetime.now().isoformat()
        if prod_info:
            # We updated prod in place: keep prod's deployment_id and endpoint.
            new_prod = {
                **test_info,
                "deployment_id": prod_info["deployment_id"],
                "endpoint": prod_info["endpoint"],
                "status": "PRODUCTION",
                "promoted_at": now,
            }
        else:
            new_prod = {**test_info, "status": "PRODUCTION", "promoted_at": now}
        
        old_prod = self.state.get("production_deployment")
        if old_prod:
            old_prod["status"] = "REPLACED"
            old_prod["replaced_at"] = now
        
        self.state["production_deployment"] = new_prod
        self.state["test_deployment"] = None
        self.state["current_version"] = test_info["version"]
        self._save_state()
        
        print(f"  ✓ v{test_info['version']} is now in production\n")
    
    def cleanup_test_deployment(self):
        """Delete the test deployment to save costs."""
        test_info = self.state.get("test_deployment")
        
        if not test_info:
            print("ℹ️  No test deployment to clean up")
            return
        
        print(f"🗑️  Deleting test deployment: {test_info['deployment_id']}")
        
        try:
            deployment = ModelDeployment.from_id(test_info["deployment_id"])
            deployment.delete(wait_for_completion=True)
            print(f"  ✓ Test deployment deleted\n")
        except Exception as e:
            print(f"  ⚠️  Could not delete deployment: {e}")
        
        self.state["test_deployment"] = None
        self._save_state()
    
    def rollback_artifacts(self, version: int) -> bool:
        """
        Rollback local artifacts to a previous version.
        
        Args:
            version: Version number to rollback to
        
        Returns:
            True if successful, False otherwise
        """
        # Find backup for this version
        backup_dirs = list(self.backup_root.glob(f"v{version}_*"))
        
        if not backup_dirs:
            print(f"❌ No backup found for v{version}")
            return False
        
        # Use the most recent backup for this version
        backup_dir = sorted(backup_dirs)[-1]
        
        print(f"⏪ Rolling back artifacts to v{version}")
        print(f"   From backup: {backup_dir}")
        
        # Remove current artifacts
        if self.artifact_dir.exists():
            shutil.rmtree(self.artifact_dir)
        
        # Restore from backup
        backup_artifacts = backup_dir / "recommender_model_artifact"
        if backup_artifacts.exists():
            shutil.copytree(backup_artifacts, self.artifact_dir)
            print(f"  ✓ Artifacts restored")
        
        # Restore results
        if self.results_dir.exists():
            shutil.rmtree(self.results_dir)
        
        backup_results = backup_dir / "results"
        if backup_results.exists():
            shutil.copytree(backup_results, self.results_dir)
            print(f"  ✓ Results restored")
        
        print(f"  ✓ Rollback complete\n")
        return True
    
    def get_deployment_summary(self) -> str:
        """Get a summary of current deployments."""
        prod = self.state.get("production_deployment")
        test = self.state.get("test_deployment")
        
        lines = ["=" * 60]
        lines.append(f"🎯 {self.project_name} - Deployment Status")
        lines.append("=" * 60)
        
        if prod:
            lines.append(f"\n✅ PRODUCTION (v{prod['version']})")
            lines.append(f"   Model: {prod['model_id']}")
            lines.append(f"   Endpoint: {prod['endpoint']}")
            lines.append(f"   Deployed: {prod.get('created_at', 'N/A')}")
        else:
            lines.append("\n⚠️  PRODUCTION: Not deployed")
        
        if test:
            lines.append(f"\n🧪 TEST (v{test['version']})")
            lines.append(f"   Model: {test['model_id']}")
            lines.append(f"   Endpoint: {test['endpoint']}")
            lines.append(f"   Created: {test.get('created_at', 'N/A')}")
        else:
            lines.append("\n🧪 TEST: No test deployment")
        
        lines.append(f"\n📊 Current Version: v{self.state['current_version']}")
        lines.append(f"📦 Total Deployments: {len(self.state['deployment_history'])}")
        lines.append("=" * 60 + "\n")
        
        return "\n".join(lines)
    
    def import_existing_deployment(
        self,
        deployment_id: str,
        model_id: str,
        endpoint: str,
        version: int = 1,
        description: str = "Imported existing deployment"
    ):
        """
        Import an existing production deployment into the management system.
        Use this on first run to track your current production model.
        
        Args:
            deployment_id: OCI deployment OCID
            model_id: OCI model OCID
            endpoint: Deployment endpoint URL
            version: Version number to assign (default: 1)
            description: Description of this deployment
        """
        print(f"📥 Importing existing deployment as v{version}...")
        
        deployment_info = {
            "deployment_id": deployment_id,
            "model_id": model_id,
            "endpoint": endpoint,
            "version": version,
            "status": "PRODUCTION",
            "created_at": datetime.now().isoformat(),
            "description": description,
            "imported": True
        }
        
        self.state["production_deployment"] = deployment_info
        self.state["current_version"] = version
        self.state["deployment_history"].append(deployment_info)
        self._save_state()
        
        print(f"  ✓ Imported v{version} as current production")
        print(f"  ✓ Model: {model_id}")
        print(f"  ✓ Endpoint: {endpoint}")
        print(f"\n✅ Next retraining will create v{version + 1}\n")
    
    def repair_production_state(
        self,
        deployment_id: str,
        model_id: str,
        endpoint: str,
        version: int = 1
    ):
        """
        Fix state after a failed promote that overwrote production_deployment
        with test info and set test_deployment=None.
        
        Use this when state says "v2 in production" but the OCI update failed,
        so production is still on v1. Overwrites production_deployment and
        current_version with the real prod values; sets test_deployment=None.
        
        Args:
            deployment_id: Real production deployment OCID (e.g. ...vebxra,
                NOT the test deployment ...jwqa).
            model_id: Model OCID actually serving in prod (v1).
            endpoint: Real production endpoint URL.
            version: Version to set (usually 1).
        
        Get model_id and endpoint from: a backup's metadata.json
        (production_deployment), or OCI Console (Model Deployment -> prod ->
        Configuration and URL).
        """
        print(f"🔧 Repairing production state to v{version}...")
        self.state["production_deployment"] = {
            "deployment_id": deployment_id,
            "model_id": model_id,
            "endpoint": endpoint,
            "version": version,
            "status": "PRODUCTION",
            "created_at": datetime.now().isoformat(),
            "repaired_at": datetime.now().isoformat(),
        }
        self.state["current_version"] = version
        self.state["test_deployment"] = None
        self._save_state()
        print(f"  ✓ production_deployment = real prod (deployment_id, endpoint)")
        print(f"  ✓ current_version = {version}")
        print(f"  ✓ test_deployment = None")
        print(f"\n✅ State repaired. Next retraining will create v{version + 1}\n")
    
    def repair_production_state_from_backup(self, version: int):
        """
        Repair state using production_deployment from a backup for the given version.
        Use when a failed promote corrupted state and you have a backup from that version.
        
        Args:
            version: Version to restore (e.g. 1).
        """
        backups = self.list_backups()
        cand = [b for b in backups if b.get("version") == version]
        if not cand:
            raise ValueError(f"No backup found for v{version}. Check backup_root or pass deployment_id/model_id/endpoint to repair_production_state().")
        b = cand[-1]
        prod = b.get("production_deployment")
        if not prod:
            raise ValueError(f"Backup for v{version} has no production_deployment. Use repair_production_state(deployment_id, model_id, endpoint, version={version}).")
        for k in ("deployment_id", "model_id", "endpoint"):
            if not prod.get(k):
                raise ValueError(f"Backup production_deployment missing '{k}'. Use repair_production_state() with manual values.")
        self.repair_production_state(
            deployment_id=prod["deployment_id"],
            model_id=prod["model_id"],
            endpoint=prod["endpoint"],
            version=version,
        )
    
    def list_backups(self) -> List[Dict]:
        """List all available backups."""
        backups = []
        
        for backup_dir in sorted(self.backup_root.iterdir()):
            if not backup_dir.is_dir():
                continue
            
            metadata_file = backup_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    metadata["backup_path"] = str(backup_dir)
                    backups.append(metadata)
        
        return backups


def print_backups(backups: List[Dict]):
    """Pretty print backup list."""
    print("=" * 60)
    print("📦 Available Backups")
    print("=" * 60)
    
    if not backups:
        print("No backups found")
        return
    
    for backup in backups:
        version = backup.get("version", "N/A")
        timestamp = backup.get("timestamp", "N/A")
        backup_date = backup.get("backup_date", "N/A")
        
        print(f"\n📌 Version {version} ({timestamp})")
        print(f"   Date: {backup_date}")
        print(f"   Path: {backup['backup_path']}")
        
        if backup.get("production_deployment"):
            prod = backup["production_deployment"]
            print(f"   Production Model: {prod.get('model_id', 'N/A')}")
    
    print("=" * 60 + "\n")
