# OCI Deployment Notes (WIP)

These notes capture our current thinking for an Oracle Cloud Infrastructure (OCI) deployment. They are **not yet implemented**, but reflect the agreed direction so we can revisit and refine later.

For overall backend/frontend architecture and data flow, see:

- [`ARCHITECTURE_DATA_FLOW.md`](./ARCHITECTURE_DATA_FLOW.md)

## Deployment Model

- **Target**: Single OCI **VM with Docker** running this app in a container, plus **Caddy** as reverse proxy and TLS terminator.
- **Container contents**:
  - Next.js frontend (port `3000`)
  - Express churn API server (port `3001`)
- **Proxy**:
  - Caddy listens on `:80`/`:443`
  - Uses `nip.io` for a convenient DNS name (e.g. `YOUR_VM_IP.nip.io`)
  - Proxies traffic to Next.js on `localhost:3000`

## Oracle ADB Integration

- Reuse the **same Oracle ADB instance** used in local development.
- In the container image:
  - Install **Oracle Instant Client (Linux)**.
  - Set `LD_LIBRARY_PATH` and `TNS_ADMIN` to the Instant Client + wallet paths.
  - Call `oracledb.initOracleClient({ libDir, configDir })` in `app/lib/db/oracle.ts`.
- On the OCI VM:
  - Mount the ADB wallet directory into the container (e.g. `-v /opt/wallet:/opt/oracle/wallet`).
  - Provide `ADB_USERNAME`, `ADB_PASSWORD`, `ADB_CONNECTION_STRING`, and `TNS_ADMIN` via env vars.

## Local vs OCI VM Responsibilities

- **Mac (local development)**:
  - No Docker required.
  - Run Next.js + Express directly with the locally installed Oracle Instant Client.
  - Code changes are committed and pushed to GitHub.

- **OCI VM**:
  - Has Docker installed.
  - Acts as both **build** and **runtime** environment for the container:
    ```bash
    git pull origin feature/churn-ml-api-backend
    docker build -t ai-demo:latest .
    docker stop ai-demo || true
    docker rm ai-demo || true
    docker run -d --name ai-demo ... ai-demo:latest
    ```
  - Caddy runs alongside the app container and forwards public traffic.

## Why Docker on OCI VM (vs bare VM)

- Avoids repeating Oracle Instant Client setup on multiple machines.
- Ensures the **same environment** used in testing runs in production.
- Simplifies rollback and upgrades: swap image tags instead of reconfiguring the VM.

## Open Questions / To Revisit

- Exact Oracle Instant Client version and installation steps in the `Dockerfile`.
- How to store and mount the wallet securely on OCI (direct file copy vs Object Storage / Vault).
- Whether to introduce OCI Container Instances later for a more managed runtime.

