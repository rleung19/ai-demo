# Current Server Status

## ✅ Both Servers Running

### Next.js Frontend
- **Status**: ✅ Running
- **Port**: 3000
- **URL**: http://localhost:3000
- **Process**: PID 42327

### Standalone API Server
- **Status**: ✅ Running  
- **Port**: 3001
- **URL**: http://localhost:3001
- **Process**: tsx watch (hot reload enabled)

## Quick Commands

### Check Status
```bash
# Check Next.js
curl http://localhost:3000

# Check API Server
curl http://localhost:3001/api/health
```

### Stop Servers
```bash
# Stop Next.js
pkill -f "next dev"

# Stop API Server
pkill -f "tsx watch server"

# Stop both
pkill -f "next dev"; pkill -f "tsx watch server"
```

### Restart Both
```bash
npm run dev:all
```

## Port Configuration

The API server now correctly uses `API_PORT` (defaults to 3001) instead of `PORT` to avoid conflicts with Next.js.

Set in `.env`:
```env
API_PORT=3001  # API server port
PORT=3000      # Next.js port (default)
```

## Testing Endpoints

**API Server (Port 3001):**
```bash
curl http://localhost:3001/api/health
curl http://localhost:3001/api/kpi/churn/summary
curl http://localhost:3001/api/kpi/churn/cohorts
```

**Next.js API Routes (Port 3000):**
```bash
curl http://localhost:3000/api/health
curl http://localhost:3000/api/kpi/churn/summary
```

Note: Next.js API routes may have Oracle connection issues (thin mode limitation).
