## OCI VM Deployment (Podman + podman-compose)

This guide describes how to deploy the app to an OCI VM using **Podman** and **podman-compose**, building the image **directly on the VM**.

Project root on the VM:

- `~/compose/demo/ecommerce-churn-ml-dashboard`

For overall architecture and data flow, see `docs/ARCHITECTURE_DATA_FLOW.md`.

---

### 1. One-time VM Setup

On your OCI VM:

```bash
ssh ubuntu@YOUR_VM_IP

# Install Podman and podman-compose (Oracle Linux example)
sudo dnf install -y podman podman-docker podman-compose

# Create directory for this project (including a wallets subdirectory)
mkdir -p ~/compose/demo/ecommerce-churn-ml-dashboard
mkdir -p ~/compose/demo/ecommerce-churn-ml-dashboard/wallets

cd ~/compose/demo/ecommerce-churn-ml-dashboard
git clone <YOUR_REPO_URL> .
```

Copy your **Oracle ADB wallet** from your Mac to the VM, for example into:

- `~/compose/demo/ecommerce-churn-ml-dashboard/wallets/Wallet_XXXX`

Ensure the wallet directory is readable by the user running Podman.

Create an env file (not committed to Git) for secrets:

```bash
cd ~/compose/demo/ecommerce-churn-ml-dashboard

cat > .env.oci << 'EOF'
ADB_USERNAME=your_adb_username
ADB_PASSWORD=your_adb_password
ADB_CONNECTION_STRING=your_tns_alias
EOF
```

---

### 2. Container Layout

The `docker/` directory contains:

- `docker/Dockerfile` – multi-stage build for the app (Next.js + Express).
- `docker/podman-compose.yml` – compose definition for the `app` service.
- `docker/README_OCI_VM_PODMAN.md` – this guide.

The initial container topology:

- **Service `app`**:
  - Next.js frontend (and Next.js API routes) on port `3000`.
  - Express churn API server on port `3001` (optional external exposure).
  - Oracle Instant Client + wallet via a mounted volume.

---

### 3. Oracle ADB Integration

- Wallet on VM:
  - `~/compose/demo/ecommerce-churn-ml-dashboard/wallets/Wallet_XXXX`
- Mounted into container at:
  - `/opt/oracle/wallet` (read-only).
- Environment variables:
  - `TNS_ADMIN=/opt/oracle/wallet`
  - `ADB_WALLET_PATH=/opt/oracle/wallet`
  - `ADB_USERNAME`, `ADB_PASSWORD`, `ADB_CONNECTION_STRING`

`app/lib/db/oracle.ts` already calls `oracledb.initOracleClient({ libDir, configDir })`; you only need to ensure:

- `libDir` points at your Instant Client (`/opt/oracle/instantclient_23_3` inside the container).
- `configDir` is `/opt/oracle/wallet`.

---

### 4. Build and Run with podman-compose

From `~/compose/demo/ecommerce-churn-ml-dashboard`:

```bash
cd ~/compose/demo/ecommerce-churn-ml-dashboard

set -a
source .env.oci
set +a

podman-compose -f docker/podman-compose.yml build app
podman-compose -f docker/podman-compose.yml up -d app
```

What this does:

- Builds the `ecommerce-churn-ml-dashboard:latest` image using `docker/Dockerfile`.
- Starts the `ecommerce-churn-ml-dashboard-app` container in the background.

You should then be able to reach (assuming security rules allow it):

- `http://YOUR_VM_IP:3000` → Next.js UI.
- `http://YOUR_VM_IP:3001/api/kpi/churn/summary` → Express churn API (if port 3001 is exposed).

For development / troubleshooting, you can also use SSH port forwarding instead of opening ports:

```bash
ssh -L 3000:localhost:3000 ubuntu@YOUR_VM_IP
```

Then visit `http://localhost:3000` from your laptop.

---

### 5. Updating After Code Changes

After you push new commits to GitHub:

```bash
ssh ubuntu@YOUR_VM_IP

cd ~/compose/demo/ecommerce-churn-ml-dashboard
git pull origin main    # or your feature branch

set -a
source .env.oci
set +a

podman-compose -f docker/podman-compose.yml build app
podman-compose -f docker/podman-compose.yml up -d app
```

Podman will reuse layers where possible; `up -d` recreates the container with the new image.

---

### 6. Optional: Caddy Integration (Reverse Proxy + TLS)

> Your VM already has **Caddy** installed and configured for other apps. This section shows how to add this app behind Caddy; adapt it to your existing `Caddyfile`.

Assuming:

- Caddy is running on the VM host (not in a container).
- You want to expose the app at `https://YOUR_VM_IP.nip.io` (or another hostname).
- The `app` container is listening on `localhost:3000` from the VM’s perspective.

Add a site block to your `Caddyfile` (example):

```caddyfile
YOUR_VM_IP.nip.io {
  reverse_proxy 127.0.0.1:3000
}
```

Then reload Caddy:

```bash
sudo systemctl reload caddy
```

Once this is wired:

- External users hit `https://YOUR_VM_IP.nip.io`.
- Caddy terminates TLS and proxies to the `app` container on `localhost:3000`.

If later you decide to run Caddy as a container as well, you can extend `docker/podman-compose.yml` with a `caddy` service and share a network with the `app` service.

---

### 7. Troubleshooting Tips

- **Container doesn’t start**:
  - Check logs:
    ```bash
    podman logs ecommerce-churn-ml-dashboard-app
    ```
- **Oracle connection errors**:
  - Verify wallet mount path in `podman-compose.yml`.
  - Confirm `TNS_ADMIN` and `ADB_CONNECTION_STRING` match a valid alias in `tnsnames.ora`.
- **Ports not reachable externally**:
  - Confirm OCI security list / network security group allows the port.
  - Consider using SSH port forwarding during early testing.

