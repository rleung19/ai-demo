# Docker Deployment Scripts

Convenient scripts for managing the ecomm container on OCI VM.

## Scripts

### `update.sh` - Update & Deploy
Pulls latest code from git, rebuilds, and restarts the container.

```bash
cd ~/compose/demo/oracle-demo-ecomm/docker
./update.sh
```

**What it does:**
1. ✅ Pulls latest code from git
2. ✅ Checks .env.oci configuration
3. ✅ Stops existing container
4. ✅ Rebuilds image with --no-cache
5. ✅ Starts new container
6. ✅ Shows logs and status

**Use when:** You've pulled new code and need to deploy.

---

### `deploy.sh` - Rebuild & Restart
Rebuilds and restarts the container (without pulling from git).

```bash
cd ~/compose/demo/oracle-demo-ecomm/docker
./deploy.sh
```

**What it does:**
1. ✅ Checks .env.oci configuration
2. ✅ Stops existing container
3. ✅ Rebuilds image with --no-cache
4. ✅ Starts new container
5. ✅ Shows logs and status

**Use when:** You've changed local files or .env.oci and need to rebuild.

---

## Quick Reference

```bash
# Most common: Update from git and deploy
./update.sh

# After changing .env.oci locally
./deploy.sh

# View live logs (note: flags before container name)
podman logs -f ecomm

# View last 50 lines
podman logs --tail=50 ecomm

# Check container status
podman ps

# Stop container manually
podman-compose -f podman-compose.yml down

# Start container manually
podman-compose -f podman-compose.yml up -d
```

## Prerequisites

Both scripts expect:
- You're in the `docker/` directory
- `.env.oci` file exists with required variables
- `NEXT_PUBLIC_API_URL` is set in `.env.oci`

**Important**: The scripts automatically export `NEXT_PUBLIC_API_URL` from `.env.oci` to the shell environment before building. This is required because Docker/Podman build arguments read from the shell environment, not from the `env_file` directive (which only applies at runtime).

## Troubleshooting

**Script not executable:**
```bash
chmod +x deploy.sh update.sh
```

**Missing .env.oci:**
```bash
cp .env.oci.example .env.oci
# Edit with your credentials
nano .env.oci
```

**Container won't start:**
```bash
# Check logs (note: flags before container name in Podman)
podman logs --tail=50 ecomm

# Check if port is in use
sudo lsof -i :3002
sudo lsof -i :3003
```

**Build fails:**
```bash
# Clean up and try again
podman-compose -f podman-compose.yml down
podman system prune -f
./deploy.sh
```
