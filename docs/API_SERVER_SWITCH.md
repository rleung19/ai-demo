# API Server Switch Documentation

## Overview

The frontend can be configured to use either:
1. **Next.js API Routes** (default) - API endpoints served by Next.js on the same port (3000)
2. **Express Standalone Server** - Separate Express server on port 3001

This allows you to compare behavior and performance between the two approaches.

## Current Configuration

The API base URL is configured in `app/lib/api/churn-api.ts`:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
```

- If `NEXT_PUBLIC_API_URL` is set, it uses that value
- Otherwise, it defaults to `'http://localhost:3001'` (Express server)

## Switching to Express Server

### Option 1: Use Current Default (Recommended)
The code is currently configured to use Express server by default. Just start both servers:

```bash
# Terminal 1: Start Express API server
npm run server:dev

# Terminal 2: Start Next.js frontend
npm run dev
```

### Option 2: Use Environment Variable
Set `NEXT_PUBLIC_API_URL` in your environment:

```bash
# In .env or .env.local
NEXT_PUBLIC_API_URL=http://localhost:3001

# Then start Next.js
npm run dev
```

## Switching to Next.js API Routes

### Option 1: Use Environment Variable (Recommended)
Set `NEXT_PUBLIC_API_URL` to empty string:

```bash
# In .env or .env.local
NEXT_PUBLIC_API_URL=

# Then start Next.js
npm run dev
```

### Option 2: Modify Code Directly
Edit `app/lib/api/churn-api.ts`:

```typescript
// Change from:
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

// To:
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';
```

Then rebuild:
```bash
npm run build
```

## Testing Both Configurations

### Express Server (Port 3001)
1. Start Express server: `npm run server:dev`
2. Start Next.js frontend: `npm run dev`
3. Open `http://localhost:3000`
4. Check Express server logs for API call frequency
5. Look for: Cleaner logs, potentially fewer duplicate calls

### Next.js API Routes (Port 3000)
1. Set `NEXT_PUBLIC_API_URL=` in environment
2. Start Next.js: `npm run dev`
3. Open `http://localhost:3000`
4. Check Next.js server logs for API call frequency
5. Look for: Next.js-specific behavior, module reload issues

## API Endpoints

Both servers provide the same endpoints:

- `GET /api/health` - Health check
- `GET /api/kpi/churn/summary` - Churn summary statistics
- `GET /api/kpi/churn/cohorts` - Cohort breakdown
- `GET /api/kpi/churn/metrics` - Model metrics
- `GET /api/kpi/churn/chart-data?type=distribution` - Chart data
- `GET /api/kpi/churn/risk-factors` - Risk factors

## Comparison Points

When comparing the two approaches, check:

1. **API Call Frequency**
   - How many times each endpoint is called on page load
   - Whether React StrictMode causes duplicate calls

2. **Connection Pool Behavior**
   - Express: Single pool creation, stable across requests
   - Next.js: May see multiple pool creations due to module reloads

3. **Logging**
   - Express: Simple request logs
   - Next.js: More verbose with compilation/render times

4. **Performance**
   - Response times
   - Connection pool efficiency
   - Memory usage

## Troubleshooting

### Express Server Not Responding
- Check if port 3001 is available: `lsof -i :3001`
- Verify Express server is running: `curl http://localhost:3001/api/health`
- Check Express server logs for errors

### Next.js API Routes Not Working
- Verify `NEXT_PUBLIC_API_URL` is empty or not set
- Check Next.js server logs
- Ensure Next.js API routes are properly built

### CORS Errors
- Express server has CORS enabled by default
- Next.js API routes don't need CORS (same origin)

## Reverting Changes

To permanently switch back to Next.js API routes:

1. Edit `app/lib/api/churn-api.ts`:
   ```typescript
   const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';
   ```

2. Remove or comment out the temporary Express server configuration

3. Rebuild: `npm run build`

## Notes

- The Express server is kept as a fallback option
- Both servers use the same database connection logic (`server/lib/db/oracle.ts` vs `app/lib/db/oracle.ts`)
- API response formats are identical between both servers
- The frontend code doesn't need to change when switching servers
