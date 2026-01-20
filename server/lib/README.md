# Database Connection Utilities

## Overview

This directory contains database connection utilities for Oracle ADB Serverless.

## Files

- `oracle.ts` - Oracle database connection pool and query utilities

## Usage

```typescript
import { executeQuery, getConnection } from '@/app/lib/db/oracle';

// Execute a query (automatically manages connection)
const result = await executeQuery('SELECT * FROM OML.USER_PROFILES');

// Or get a connection for multiple queries
const connection = await getConnection();
try {
  // Use connection
} finally {
  await connection.close();
}
```

## Connection Pooling

The module automatically creates and manages a connection pool:
- Min connections: 2
- Max connections: 10
- Connection timeout: 60 seconds
- Queue timeout: 60 seconds

## Environment Variables Required

- `ADB_WALLET_PATH` - Path to Oracle wallet directory
- `ADB_CONNECTION_STRING` - Database connection string (TNS alias or full DSN)
- `ADB_USERNAME` - Database username (default: OML)
- `ADB_PASSWORD` - Database password
- `TNS_ADMIN` - Automatically set to ADB_WALLET_PATH if not provided

## Oracle Client Initialization

The module attempts to initialize Oracle client in thick mode (for wallet support):
1. Tries to find Oracle Instant Client in common locations
2. Falls back to thin mode if Instant Client not found (limited wallet support)

## Error Handling

All database operations throw errors that should be caught by API route handlers.
The API routes return appropriate HTTP status codes (503 for service unavailable).
