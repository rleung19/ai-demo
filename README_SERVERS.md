# Quick Start: Running Both Servers

## Start Everything

```bash
npm run dev:all
```

This starts both:
- **Next.js Frontend** on `http://localhost:3000`
- **API Server** on `http://localhost:3001`

Press `Ctrl+C` to stop both.

## Start Separately

**Terminal 1 - API Server:**
```bash
npm run server:dev
```

**Terminal 2 - Next.js:**
```bash
npm run dev
```

## Configuration

Set ports in `.env`:
```env
API_PORT=3001  # API server port
PORT=3000      # Next.js port
```

See `docs/STARTING_SERVERS.md` for detailed instructions.
