# Starting the Application

## Overview

The application consists of two servers:
1. **Next.js Frontend** - Runs on port 3000 (default)
2. **Standalone API Server** - Runs on port 3001 (default, configurable)

## Quick Start

### Option 1: Start Both Servers Together (Recommended)

**macOS/Linux:**
```bash
chmod +x scripts/start-all.sh
./scripts/start-all.sh
```

**Windows (PowerShell):**
```powershell
.\scripts\start-all.ps1
```

This starts both servers and shows logs. Press `Ctrl+C` to stop both.

### Option 2: Start Servers Separately

**Terminal 1 - API Server:**
```bash
npm run server:dev
```
API server runs on `http://localhost:3001`

**Terminal 2 - Next.js Frontend:**
```bash
npm run dev
```
Frontend runs on `http://localhost:3000`

## Configuration

### Environment Variables

Both servers use the same `.env` file:

```env
# Database Configuration
ADB_WALLET_PATH=/path/to/wallet
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_medium
ADB_USERNAME=OML
ADB_PASSWORD=your_password
TNS_ADMIN=/path/to/wallet  # Optional, auto-set from ADB_WALLET_PATH

# Server Ports (Optional)
API_PORT=3001              # API server port (default: 3001)
PORT=3000                  # Next.js port (default: 3000)
```

### Port Configuration

**Change API Server Port:**
```bash
API_PORT=8080 npm run server:dev
```

**Change Next.js Port:**
```bash
PORT=8080 npm run dev
```

Or add to `.env`:
```env
API_PORT=8080
PORT=8080
```

## Integration

### Option 1: Next.js API Routes (Current)

Next.js API routes are at:
- `http://localhost:3000/api/health`
- `http://localhost:3000/api/kpi/churn/*`

**Note**: These may have Oracle connection issues in Next.js dev mode.

### Option 2: Standalone API Server (Recommended)

Standalone API server endpoints:
- `http://localhost:3001/api/health`
- `http://localhost:3001/api/kpi/churn/*`

**To use standalone API with Next.js frontend:**

1. **Update `next.config.ts`** to proxy API requests:
```typescript
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/kpi/churn/:path*',
        destination: 'http://localhost:3001/api/kpi/churn/:path*',
      },
      {
        source: '/api/health',
        destination: 'http://localhost:3001/api/health',
      },
    ];
  },
};
```

2. **Or update API client** to point to standalone server:
```typescript
// app/lib/api/churn-api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
```

## Testing

### Test API Server
```bash
curl http://localhost:3001/api/health
curl http://localhost:3001/api/kpi/churn/summary
```

### Test Next.js Frontend
```bash
# Open in browser
open http://localhost:3000

# Or test API routes
curl http://localhost:3000/api/health
```

## Logs

### When Using Start Script

- **API Server logs**: `/tmp/api-server.log` (macOS/Linux)
- **Next.js logs**: `/tmp/nextjs.log` (macOS/Linux)

### When Running Separately

Logs appear in the terminal where each server is running.

## Troubleshooting

### Port Already in Use

**Change API port:**
```bash
API_PORT=3002 npm run server:dev
```

**Change Next.js port:**
```bash
PORT=3002 npm run dev
```

### API Server Not Starting

1. Check if port is available:
   ```bash
   lsof -i :3001  # macOS/Linux
   netstat -ano | findstr :3001  # Windows
   ```

2. Check logs:
   ```bash
   tail -f /tmp/api-server.log
   ```

### Next.js Not Starting

1. Check if port 3000 is available
2. Check `.next` directory - try deleting it and rebuilding:
   ```bash
   rm -rf .next
   npm run dev
   ```

### Database Connection Issues

Both servers use the same database connection code. If one works, both should work.

**Test standalone connection:**
```bash
node scripts/test-node-connection.js
```

## Production

### Build and Start

**API Server:**
```bash
npm run server:build
API_PORT=3001 npm run server:start
```

**Next.js:**
```bash
npm run build
npm start
```

### Using PM2 (Process Manager)

```bash
# Install PM2
npm install -g pm2

# Start API server
pm2 start dist/server/index.js --name churn-api

# Start Next.js
pm2 start npm --name nextjs -- start

# View status
pm2 status

# View logs
pm2 logs
```

## Summary

- **Development**: Use `./scripts/start-all.sh` to start both servers
- **API Server**: Port 3001 (configurable via `API_PORT`)
- **Next.js**: Port 3000 (configurable via `PORT`)
- **Integration**: Use Next.js rewrites or update API client to point to standalone server
