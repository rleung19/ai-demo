# Podman Cleanup Commands

## Quick Cleanup (for stuck containers/pods)

If you get errors like "containers are running" or "network is being used", use these commands:

```bash
# Stop and force remove the container
podman stop ecomm
podman rm -f ecomm

# Remove the pod (if it exists)
podman pod rm -f <pod-id>
# Or list and remove all pods
podman pod ls
podman pod rm -f $(podman pod ls -q)

# Remove the network
podman network rm -f docker_default

# Then start fresh
cd ~/compose/demo/oracle-demo-ecomm/docker
podman-compose -f podman-compose.yml build app
podman-compose -f podman-compose.yml up -d app
```

## Complete Cleanup (nuclear option)

If you need to completely clean up everything:

```bash
# Stop all containers
podman stop --all

# Remove all containers
podman rm -f --all

# Remove all pods
podman pod rm -f --all

# Remove all networks (except default)
podman network prune -f

# Remove all images (optional - will need to rebuild)
# podman rmi --all

# Start fresh
cd ~/compose/demo/oracle-demo-ecomm/docker
podman-compose -f podman-compose.yml build app
podman-compose -f podman-compose.yml up -d app
```

## Proper Shutdown Sequence

To avoid these issues in the future:

```bash
cd ~/compose/demo/oracle-demo-ecomm/docker

# Method 1: Use podman-compose down
podman-compose -f podman-compose.yml down

# If that fails, use force:
podman-compose -f podman-compose.yml down --remove-orphans

# Method 2: Manual cleanup
podman stop ecomm
podman rm ecomm
```

## Check Status

```bash
# List running containers
podman ps

# List all containers (including stopped)
podman ps -a

# List pods
podman pod ls

# List networks
podman network ls

# Check logs
podman logs ecomm
```
