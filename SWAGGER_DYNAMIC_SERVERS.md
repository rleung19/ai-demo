# Dynamic Swagger Server URLs

## How It Works

The Swagger UI now shows **context-appropriate server URLs** based on how you access it.

### Local Development

When you access Swagger at `http://localhost:3001/api-docs`:

```
Server dropdown shows:
┌─────────────────────────────────────────┐
│ ✓ Local Development (current)          │
│   http://localhost:3001                 │
└─────────────────────────────────────────┘
```

**Only localhost:3001** - no confusion with production URLs! ✅

### Production (via Public Domain)

When you access Swagger at `https://ecomm-api.40b5c371.nip.io/api-docs`:

```
Server dropdown shows:
┌─────────────────────────────────────────┐
│ ✓ Current server (production)          │
│   https://ecomm-api.40b5c371.nip.io    │
└─────────────────────────────────────────┘
```

**Only the public URL** - API calls work directly from browser! ✅

## Technical Implementation

### Dynamic Server Detection

**File**: `server/openapi.ts`

```typescript
function getServerUrls(req?: Request) {
  const servers = [];
  const host = req?.get('host');
  const protocol = req?.protocol || 'http';
  const forwardedProto = req?.get('x-forwarded-proto');
  const actualProtocol = forwardedProto || protocol;
  
  // Production access (non-localhost)
  if (host && !host.includes('localhost')) {
    servers.push({
      url: `${actualProtocol}://${host}`,
      description: 'Current server (production)',
    });
  }
  
  // Local development (localhost)
  if (host && host.includes('localhost')) {
    const port = host.split(':')[1];
    servers.push({
      url: `http://localhost:${port}`,
      description: 'Local Development (current)',
    });
  }
  
  return servers;
}
```

### Request-Based Generation

**File**: `server/index.ts`

```typescript
// Dynamic Swagger UI
app.use('/api-docs', swaggerUi.serve);
app.get('/api-docs', (req, res) => {
  const spec = generateOpenApiSpec(req);  // ← Uses request host
  const html = swaggerUi.generateHTML(spec);
  res.send(html);
});

// Dynamic OpenAPI JSON
app.get('/openapi.json', (req, res) => {
  res.json(generateOpenApiSpec(req));     // ← Uses request host
});
```

## Examples

### Example 1: Local Development

**Access**: `http://localhost:3001/api-docs`

**Request headers**:
```
Host: localhost:3001
```

**Generated servers**:
```json
[
  {
    "url": "http://localhost:3001",
    "description": "Local Development (current)"
  }
]
```

### Example 2: Production Access

**Access**: `https://ecomm-api.40b5c371.nip.io/api-docs`

**Request headers** (via Caddy):
```
Host: ecomm-api.40b5c371.nip.io
X-Forwarded-Proto: https
```

**Generated servers**:
```json
[
  {
    "url": "https://ecomm-api.40b5c371.nip.io",
    "description": "Current server (production)"
  }
]
```

### Example 3: SSH Port Forwarding

**Setup**: `ssh -L 3003:localhost:3003 user@vm`  
**Access**: `http://localhost:3003/api-docs`

**Request headers**:
```
Host: localhost:3003
```

**Generated servers**:
```json
[
  {
    "url": "http://localhost:3003",
    "description": "Local Development (current)"
  }
]
```

## Benefits

1. ✅ **No confusion** - Only shows relevant URLs
2. ✅ **Works automatically** - No configuration needed
3. ✅ **Correct by default** - "Try it out" just works
4. ✅ **Secure** - Public URL doesn't expose localhost options
5. ✅ **Developer friendly** - Local dev only sees local options

## Fallback Behavior

If no request context is available (edge case), shows:
- Production URL from `NEXT_PUBLIC_API_URL` env var (if set)
- `http://localhost:3001` (local development)

This ensures Swagger always has at least one working server URL.
