## OCI VM Deployment (Podman + podman-compose)

This guide describes how to deploy the app to an OCI VM using **Podman** and **podman-compose**, building the image **directly on the VM**.

Project root on the VM:

- `~/compose/demo/oracle-demo-ecomm`

For overall architecture and data flow, see `docs/ARCHITECTURE_DATA_FLOW.md`.

---

### 1. One-time VM Setup

On your OCI VM:

```bash
ssh ubuntu@YOUR_VM_IP

# Install Podman and podman-compose (Oracle Linux example)
sudo dnf install -y podman podman-docker podman-compose

# Create directory for this project
mkdir -p ~/compose/demo/oracle-demo-ecomm

cd ~/compose/demo/oracle-demo-ecomm

# IMPORTANT: clone *into* the current directory (note the final dot)
git clone https://github.com/rleung19/ai-demo.git .

# Create a wallets directory inside the project (this path is in .gitignore)
mkdir -p wallets/Wallet_HHZJ2H81DDJWN1DM

# REQUIRED: Download and unpack the Oracle Instant Client basic package.
# The Dockerfile expects the Instant Client to be located at /opt/oracle on the host.
#
# Steps:
#   1. Download instantclient-basic-linux.x64-23.26*.zip from Oracle
#   2. Copy it to the VM (e.g., via scp)
#   3. Create the directory and unzip:
#      sudo mkdir -p /opt/oracle
#      sudo unzip instantclient-basic-linux.x64-23.26*.zip -d /opt/oracle
#   4. The final structure should be:
#      /opt/oracle/instantclient_23_26/
#        libclntsh.so
#        libocci.so
#        ... (other Instant Client files)
#
# Note: The Dockerfile copies from ../opt/oracle (relative to project root),
# which resolves to /opt/oracle on the host when the build context is the project root.
```

Copy your **Oracle ADB wallet** from your Mac to the VM into:

- `~/compose/demo/oracle-demo-ecomm/wallets/Wallet_HHZJ2H81DDJWN1DM`

Ensure the wallet directory is readable by the user running Podman. The `podman-compose.yml` uses a relative path `../wallets/Wallet_HHZJ2H81DDJWN1DM` which resolves to this location.

Create an env file (not committed to Git) for secrets (used by `podman-compose` via `env_file` in the `docker` directory):

```bash
cd ~/compose/demo/oracle-demo-ecomm/docker

cat > .env.oci << 'EOF'
ADB_USERNAME=your_adb_username
ADB_PASSWORD=your_adb_password
ADB_CONNECTION_STRING=your_tns_alias

# OCI Model Deployment Endpoints (for recommender APIs)
# Obtain these from your OCI Data Science Notebook deployment cells
# Format: https://modeldeployment.{region}.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.{region}.{id}
# Do NOT include the /predict suffix
OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT=https://modeldeployment.us-chicago-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.us-chicago-1.abc123xyz
OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT=https://modeldeployment.us-chicago-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.us-chicago-1.def456uvw
EOF
```

See `docker/.env.oci.example` for a template with detailed comments.

---

### 2. Container Layout

The `docker/` directory contains:

- `docker/Dockerfile` – multi-stage build for the app (Next.js + Express).
- `docker/podman-compose.yml` – compose definition for the `app` service.
- `docker/README_OCI_VM_PODMAN.md` – this guide.

The initial container topology:

- **Service `app`**:
  - Next.js frontend (and Next.js API routes) exposed on host port `3002` (container port `3000`).
  - Express churn API server exposed on host port `3003` (container port `3001`, optional external exposure).
  - Oracle Instant Client + wallet via a mounted volume.
  - **Note**: The container runs `npm run dev:all` which starts both Next.js and Express in development/watch mode. This is suitable for a demo environment.

---

### 3. Oracle ADB Integration

- Wallet on VM:
  - `~/compose/demo/oracle-demo-ecomm/wallets/Wallet_HHZJ2H81DDJWN1DM`
- Mounted into container at:
  - `/opt/oracle/wallet` (read-only, using relative path `../wallets/Wallet_HHZJ2H81DDJWN1DM`).
- Environment variables:
  - `TNS_ADMIN=/opt/oracle/wallet`
  - `ADB_WALLET_PATH=/opt/oracle/wallet`
  - `ADB_USERNAME`, `ADB_PASSWORD`, `ADB_CONNECTION_STRING`

`app/lib/db/oracle.ts` already calls `oracledb.initOracleClient({ libDir, configDir })`; you only need to ensure:

- `libDir` points at your Instant Client (`/opt/oracle/instantclient_23_26` inside the container).
- `configDir` is `/opt/oracle/wallet`.

---

### 3.5 OCI Model Deployment Configuration

The recommender APIs (`/api/recommender/product` and `/api/recommender/basket`) require OCI authentication to call the deployed model endpoints. The container uses a **project-local `.oci` directory** (sibling to `wallets/`) that is mounted into the container.

#### Setup OCI Config and API Key

On the VM, create the `.oci` directory in the project root:

```bash
cd ~/compose/demo/oracle-demo-ecomm

# Create .oci directory (sibling to wallets/)
mkdir -p .oci

# Create OCI config file
cat > .oci/config << 'EOF'
[DEFAULT]
user=ocid1.user.oc1..aaaaaaa...
fingerprint=aa:bb:cc:dd:ee:ff:11:22:33:44:55:66:77:88:99:aa
tenancy=ocid1.tenancy.oc1..aaaaaaa...
region=us-chicago-1
key_file=/root/.oci/oci_api_key.pem
pass_phrase=your_api_key_passphrase_if_any
EOF

# Copy your OCI API private key to .oci/oci_api_key.pem
# (You can generate this key pair in OCI Console: Identity > Users > API Keys)
cp /path/to/your/oci_api_key.pem .oci/oci_api_key.pem

# Set appropriate permissions
chmod 600 .oci/config
chmod 600 .oci/oci_api_key.pem
```

**Important**: The `key_file` path in the config must be `/root/.oci/oci_api_key.pem` (the container path), not the host path.

#### Obtain Model Deployment Endpoint URLs

1. Open your OCI Data Science Notebook session where you deployed the models.
2. For the **Product Recommender** (from `Recommender-2.ipynb`):
   - Find the cell that calls `deployment.predict(...)` or shows the deployment URL.
   - Copy the base URL (without `/predict` suffix).
   - Example: `https://modeldeployment.us-chicago-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.us-chicago-1.abc123xyz`
3. For the **Basket Recommender** (from `Basket-2.ipynb`):
   - Similarly, find the deployment URL from the notebook.
   - Copy the base URL (without `/predict` suffix).

Add these URLs to `docker/.env.oci`:

```bash
OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT=https://modeldeployment.us-chicago-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.us-chicago-1.abc123xyz
OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT=https://modeldeployment.us-chicago-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.us-chicago-1.def456uvw
```

The `podman-compose.yml` mounts `../.oci` (project-local) to `/root/.oci` in the container (read-only), so the OCI SDK can read the config and API key from inside the container.

#### Troubleshooting OCI Authentication

If the recommender APIs return `503 OCI service error`:

1. **Verify config file exists and is readable**:
   ```bash
   ls -la ~/compose/demo/oracle-demo-ecomm/.oci/config
   cat ~/compose/demo/oracle-demo-ecomm/.oci/config
   ```

2. **Verify API key file exists and permissions**:
   ```bash
   ls -la ~/compose/demo/oracle-demo-ecomm/.oci/oci_api_key.pem
   # Should show -rw------- (600)
   ```

3. **Verify volume mount is working** (check container logs):
   ```bash
   podman logs ecomm | grep -i oci  # Note: pipe works without flags
   # Or exec into container:
   podman exec -it ecomm ls -la /root/.oci
   ```

4. **Verify endpoint URLs are correct**:
   - Check that the URLs in `.env.oci` match the deployment URLs from your notebooks.
   - Ensure they don't include the `/predict` suffix.
   - Test the endpoint directly (from the VM) using `curl` with OCI authentication if needed.

5. **Check OCI API key permissions**:
   - Ensure the API key user has permissions to invoke the model deployment endpoints.
   - Verify the key hasn't expired or been revoked in OCI Console.

---

### 4. Build and Run with podman-compose

From `~/compose/demo/oracle-demo-ecomm/docker`:

```bash
cd ~/compose/demo/oracle-demo-ecomm/docker

podman-compose -f podman-compose.yml build app
podman-compose -f podman-compose.yml up -d app
```

What this does:

- Builds the `ecomm:latest` image using `docker/Dockerfile`.
- Starts the `ecomm` container in the background.

You should then be able to reach (assuming security rules allow it):

- `http://YOUR_VM_IP:3002` → Next.js UI.
- `http://YOUR_VM_IP:3003/api/kpi/churn/summary` → Express churn API (if port 3003 is exposed).
- `http://YOUR_VM_IP:3003/api/recommender/product` → Product recommender API (POST with `{"user_id": "...", "top_k": 5}`).
- `http://YOUR_VM_IP:3003/api/recommender/basket` → Basket recommender API (POST with `{"basket": ["B01CG1J7XG", ...], "top_n": 3}`).

**Note**: The container is configured with `NEXT_PUBLIC_API_URL=https://ecomm.40b5c371.nip.io`, which means the frontend will make API calls to this URL. Ensure your Caddy reverse proxy is configured to route this domain to the container (see Section 6).

For development / troubleshooting, you can also use SSH port forwarding instead of opening ports:

```bash
ssh -L 3002:localhost:3002 -L 3003:localhost:3003 ubuntu@YOUR_VM_IP
```

Then visit `http://localhost:3002` from your laptop.

---

### 5. Updating After Code Changes

After you push new commits to GitHub:

```bash
ssh ubuntu@YOUR_VM_IP

cd ~/compose/demo/oracle-demo-ecomm
git pull origin main    # or your feature branch

cd docker
podman-compose -f podman-compose.yml build app
podman-compose -f podman-compose.yml up -d app
```

Podman will reuse layers where possible; `up -d` recreates the container with the new image.

---

### 6. Optional: Caddy Integration (Reverse Proxy + TLS)

> Your VM already has **Caddy** installed and configured for other apps. This section shows how to add this app behind Caddy; adapt it to your existing `Caddyfile`.

Assuming:

- Caddy is running on the VM host (not in a container).
- You want to expose the app at `https://ecomm.40b5c371.nip.io` (matching the `NEXT_PUBLIC_API_URL` in `podman-compose.yml`).
- The `app` container is listening on `localhost:3002` from the VM's perspective (host port mapped to container port 3000).

Add a site block to your `Caddyfile`:

```caddyfile
ecomm.40b5c371.nip.io {
  reverse_proxy 127.0.0.1:3002
}
```

Then reload Caddy:

```bash
sudo systemctl reload caddy
```

Once this is wired:

- External users hit `https://ecomm.40b5c371.nip.io`.
- Caddy terminates TLS and proxies to the `ecomm` container on `localhost:3002`.
- The frontend will make API calls to `https://ecomm.40b5c371.nip.io` (as configured in `NEXT_PUBLIC_API_URL`).

If later you decide to run Caddy as a container as well, you can extend `docker/podman-compose.yml` with a `caddy` service and share a network with the `app` service.

---

### 7. Troubleshooting

#### 7.1 Cleanup: Remove Existing Containers/Pods/Networks

If you encounter errors like "container is running" or "network is being used", clean up first:

```bash
cd ~/compose/demo/oracle-demo-ecomm/docker

# Stop and remove the container (force if needed)
podman stop ecomm 2>/dev/null || true
podman rm -f ecomm 2>/dev/null || true

# List all pods and remove them
podman pod ps
# Remove any pods (replace <pod-id> with actual pod ID from above)
podman pod rm -f <pod-id> 2>/dev/null || true

# Or remove all stopped containers and pods
podman container prune -f
podman pod prune -f

# Remove the network if it exists (force if needed)
podman network rm -f docker_default 2>/dev/null || true

# Now try starting again
podman-compose -f podman-compose.yml build app
podman-compose -f podman-compose.yml up -d app
```

#### 7.2 Port Already in Use

If you see `bind: address already in use` for port 3002 or 3003:

```bash
# Check what's using the port
sudo lsof -i :3002
sudo lsof -i :3003
# or
sudo netstat -tlnp | grep 3002
sudo netstat -tlnp | grep 3003

# If it's another service, either:
# Option A: Stop that service temporarily
sudo systemctl stop <service-name>

# Option B: Change the host port in podman-compose.yml
# Edit docker/podman-compose.yml and change "3002:3000" to another port
```

#### 7.3 Container Doesn't Start

Check logs:

```bash
podman logs ecomm
```

#### 7.4 Oracle Connection Errors

- Verify wallet mount path in `podman-compose.yml` matches the actual wallet location on the VM.
- Confirm `TNS_ADMIN` and `ADB_CONNECTION_STRING` match a valid alias in `tnsnames.ora`.
- Check that the wallet directory is readable:
  ```bash
  ls -la ~/compose/demo/oracle-demo-ecomm/wallets/Wallet_HHZJ2H81DDJWN1DM
  ```
- Verify the Oracle Instant Client is accessible at `/opt/oracle/instantclient_23_26` on the host:
  ```bash
  ls -la /opt/oracle/instantclient_23_26
  ```

#### 7.5 Ports Not Reachable Externally

- Confirm OCI security list / network security group allows the port.
- Check firewall rules on the VM:
  ```bash
  sudo firewall-cmd --list-all
  ```
- Consider using SSH port forwarding during early testing:
  ```bash
  ssh -L 3002:localhost:3002 -L 3003:localhost:3003 ubuntu@YOUR_VM_IP
  ```

