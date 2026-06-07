# OCI Deployment (Docker Compose)

Deploy the **Next.js UI + Express churn API** to an OCI VM using Docker Compose or Podman Compose.

```
Browser → Caddy (TLS) → :3002 Next.js UI
                      → :3003 Express API (churn KPIs, recommender)
                              │
                    DB_BACKEND=oracle | postgres
                              │
                    ADB wallet    or    OCI Postgres (VCN)
```

Churn KPIs are **Express-only** — the container does not run Next.js `/api/kpi/churn` routes.

---

## Prerequisites (VM)

| Item | Oracle (`DB_BACKEND=oracle`) | Postgres (`DB_BACKEND=postgres`) |
|------|------------------------------|----------------------------------|
| Runtime | Docker Compose or Podman Compose | Same |
| Instant Client | `opt/oracle/instantclient_23_26/` at project root | Not required at runtime* |
| ADB wallet | `wallets/Wallet_HHZJ2H81DDJWN1DM/` | Not required |
| OCI SDK | `.oci/` for recommender APIs | Same |
| Network | Outbound to ADB | VCN access to Postgres private IP |

\*Instant Client is still baked into the image; use `docker-compose.postgres.yml` to skip wallet mount.

**Suggested VM layout:**

```
~/compose/demo/oracle-demo-ecomm/
├── app/ server/ docker/ ...
├── docker/.env.oci          # secrets (not in git)
├── wallets/...              # oracle only
├── opt/oracle/instantclient_23_26/   # oracle only (for image build)
└── .oci/                    # recommender API credentials
```

---

## One-time setup

```bash
ssh ubuntu@YOUR_VM_IP

# Docker (Ubuntu)
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER

# — or Podman (Oracle Linux) —
# sudo dnf install -y podman podman-docker podman-compose

mkdir -p ~/compose/demo/oracle-demo-ecomm
cd ~/compose/demo/oracle-demo-ecomm
git clone https://github.com/rleung19/ai-demo.git .
git checkout feature/postgres-backend   # or your deploy branch

cd docker
cp .env.oci.example .env.oci
nano .env.oci
```

---

## Configure `.env.oci`

### Oracle ADB (workshop default)

```env
DB_BACKEND=oracle
NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io
ADB_WALLET_PATH=/opt/oracle/wallet
TNS_ADMIN=/opt/oracle/wallet
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_medium
ADB_USERNAME=OML
ADB_PASSWORD=...
```

### PostgreSQL (OCI Postgres in VCN)

```env
DB_BACKEND=postgres
NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io
PGHOST=10.0.1.239
PGPORT=5432
PGUSER=ecomm
PGPASSWORD=...
PGDATABASE=ecommdb
PGSSLMODE=require
```

Ensure the VM security list / NSG allows the compute instance → Postgres on port 5432.

---

## Deploy

From `docker/`:

```bash
chmod +x deploy.sh update.sh
./deploy.sh
```

`deploy.sh` picks compose overrides from `DB_BACKEND` in `.env.oci`:

| Backend | Compose command (equivalent) |
|---------|------------------------------|
| `oracle` | `docker compose -f docker-compose.yml -f docker-compose.oracle.yml up -d --build` |
| `postgres` | `docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d --build` |

Manual:

```bash
export $(grep '^NEXT_PUBLIC_API_URL=' .env.oci | xargs)
docker compose -f docker-compose.yml -f docker-compose.oracle.yml build --no-cache
docker compose -f docker-compose.yml -f docker-compose.oracle.yml up -d
```

---

## Verify

```bash
curl -s http://localhost:3003/api/health | python3 -m json.tool
curl -s http://localhost:3003/api/kpi/churn/summary | python3 -m json.tool
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3002/
```

Health should show `"backend": "oracle"` or `"postgres"` and `"connected": true`.

---

## Caddy (production URLs)

Typical split on the VM:

| Public URL | Proxy to |
|------------|----------|
| `https://ecomm.40b5c371.nip.io` | `localhost:3002` (UI) |
| `https://ecomm-api.40b5c371.nip.io` | `localhost:3003` (Express) |

`NEXT_PUBLIC_API_URL` must match the public API hostname (build-time variable).

---

## Container internals

- **CMD**: `npm run start:all` → Express (`dist/server/index.js` :3001) + Next.js (`next start` :3000)
- **Host ports**: `3002:3000`, `3003:3001`
- **Healthcheck**: `GET http://127.0.0.1:3001/api/health`

---

## Update from git

```bash
cd ~/compose/demo/oracle-demo-ecomm/docker
./update.sh    # git pull + deploy.sh
```

Edit `update.sh` if you deploy from a branch other than `main`.

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| UI loads, no KPI data | `NEXT_PUBLIC_API_URL` matches public API URL; rebuild after changing it |
| Oracle `DPI-1047` | Instant Client in `opt/oracle/` before build; wallet mounted |
| Postgres timeout | VM can reach `PGHOST:PGPORT`; security lists / NSG |
| Build missing `NEXT_PUBLIC_*` | `deploy.sh` exports from `.env.oci` before build |

See also: [README_OCI_VM_PODMAN.md](README_OCI_VM_PODMAN.md), [docs/POSTGRES_MIGRATION.md](../docs/POSTGRES_MIGRATION.md)
