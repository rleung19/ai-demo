# Docker Setup Backup - 2026-01-25

## What's Backed Up

This backup was created before optimizing the Dockerfile to remove Oracle Instant Client from the build stage.

**Backed up files:**
- `Dockerfile` - Multi-stage build configuration
- `podman-compose.yml` - Container orchestration
- `deploy.sh` - Deployment script
- `update.sh` - Update and deploy script
- `SCRIPTS.md` - Script documentation
- `.env.oci.example` - Environment variable template

## How to Restore

If you need to restore the original Docker setup:

```bash
# Navigate to docker directory
cd ~/Projects/aiworkshop2026/ai-demo/docker

# Restore all files from backup
cp backup/2026-01-25-before-dockerfile-optimization/Dockerfile ./
cp backup/2026-01-25-before-dockerfile-optimization/podman-compose.yml ./
cp backup/2026-01-25-before-dockerfile-optimization/deploy.sh ./
cp backup/2026-01-25-before-dockerfile-optimization/update.sh ./
cp backup/2026-01-25-before-dockerfile-optimization/SCRIPTS.md ./
cp backup/2026-01-25-before-dockerfile-optimization/.env.oci.example ./

# Restore permissions
chmod +x deploy.sh update.sh

# Verify
git status
```

Or restore selectively:

```bash
# Restore only Dockerfile
cp backup/2026-01-25-before-dockerfile-optimization/Dockerfile ./

# Restore and rebuild
podman-compose -f podman-compose.yml build --no-cache
```

## Quick Restore (One Command)

```bash
cd ~/Projects/aiworkshop2026/ai-demo/docker && \
cp backup/2026-01-25-before-dockerfile-optimization/* ./ && \
chmod +x deploy.sh update.sh && \
echo "✅ Restored from backup"
```

## What Changed After This Backup

The Dockerfile was optimized to:
- Remove Oracle Instant Client from builder stage (lines 13-16)
- Remove redundant Oracle copy in final stage (line 33)
- Copy only necessary build artifacts (.next, dist, public) from builder
- Keep Oracle Instant Client only in final runtime stage

**Result**: Faster builds, smaller intermediate images, clearer separation of concerns.

## Rollback Strategy on OCI VM

If the optimized Dockerfile causes issues in production:

```bash
# SSH to OCI VM
ssh ubuntu@your-vm-ip

# Navigate to project
cd ~/compose/demo/oracle-demo-ecomm

# Pull this backup
git pull origin main

# Restore from backup
cd docker
cp backup/2026-01-25-before-dockerfile-optimization/Dockerfile ./

# Rebuild with original Dockerfile
podman-compose -f podman-compose.yml down
podman-compose -f podman-compose.yml build --no-cache
podman-compose -f podman-compose.yml up -d

# Verify
podman logs --tail=50 ecomm
```

## Verification

After restore, verify files match:

```bash
diff Dockerfile backup/2026-01-25-before-dockerfile-optimization/Dockerfile
# Should show no differences if restored correctly
```

## Backup Location

This backup is committed to git, so you can access it from any clone:
```
docker/backup/2026-01-25-before-dockerfile-optimization/
```

---

**Created**: 2026-01-25  
**Reason**: Before Dockerfile optimization (remove Oracle from build stage)  
**Safe to delete**: After confirming optimized version works in production
