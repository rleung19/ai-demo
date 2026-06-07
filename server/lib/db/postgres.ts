/**
 * PostgreSQL connection pool for churn API (ecomm schema)
 */

import pg from 'pg';

const { Pool } = pg;

let pool: pg.Pool | null = null;

function resolveSsl(): boolean | { rejectUnauthorized: boolean } | undefined {
  const url = process.env.DATABASE_URL || '';
  const mode = (process.env.PGSSLMODE || '').toLowerCase();

  if (mode === 'disable' || url.includes('sslmode=disable')) {
    return undefined;
  }

  // OCI Postgres through SSH tunnel typically requires TLS (node pg vs psycopg2)
  return { rejectUnauthorized: false };
}

function getPoolConfig(): pg.PoolConfig {
  const ssl = resolveSsl();
  const url = process.env.DATABASE_URL;
  if (url) {
    return { connectionString: url, max: 5, idleTimeoutMillis: 30000, ssl };
  }

  if (!process.env.PGUSER || !process.env.PGPASSWORD || !process.env.PGDATABASE) {
    throw new Error(
      'Postgres config missing: set DATABASE_URL or PGUSER, PGPASSWORD, PGDATABASE'
    );
  }

  return {
    host: process.env.PGHOST || '127.0.0.1',
    port: parseInt(process.env.PGPORT || '5432', 10),
    user: process.env.PGUSER,
    password: process.env.PGPASSWORD,
    database: process.env.PGDATABASE,
    max: 5,
    idleTimeoutMillis: 30000,
    ssl,
  };
}

export async function getPool(): Promise<pg.Pool> {
  if (!pool) {
    pool = new Pool(getPoolConfig());
    pool.on('error', (err) => {
      console.error('Postgres pool error:', err.message);
    });
    console.log('✓ Postgres connection pool created');
  }
  return pool;
}

function convertNamedParams(
  sql: string,
  binds?: Record<string, unknown>
): { text: string; values: unknown[] } {
  if (!binds || Object.keys(binds).length === 0) {
    return { text: sql, values: [] };
  }

  const values: unknown[] = [];
  const indexByName = new Map<string, number>();

  const text = sql.replace(/:([a-zA-Z_][a-zA-Z0-9_]*)/g, (_match, name: string) => {
    if (!indexByName.has(name)) {
      if (!(name in binds)) {
        throw new Error(`Missing bind parameter: ${name}`);
      }
      indexByName.set(name, values.length + 1);
      values.push(binds[name]);
    }
    return `$${indexByName.get(name)}`;
  });

  return { text, values };
}

function uppercaseRow(row: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(row)) {
    out[key.toUpperCase()] = value;
  }
  return out;
}

export async function executeQuery<T = Record<string, unknown>>(
  query: string,
  binds?: Record<string, unknown>
): Promise<{ rows: T[] }> {
  const poolInstance = await getPool();
  const { text, values } = convertNamedParams(query, binds);
  const result = await poolInstance.query(text, values);
  return {
    rows: result.rows.map((row) => uppercaseRow(row) as T),
  };
}

export async function initializePool(): Promise<void> {
  try {
    await getPool();
    const ok = await testConnection();
    if (ok) {
      console.log('✓ Postgres pool initialized and ready');
    }
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error('❌ Failed to initialize Postgres pool:', message);
  }
}

export async function closePool(): Promise<void> {
  if (pool) {
    await pool.end();
    pool = null;
    console.log('✓ Postgres connection pool closed');
  }
}

export async function testConnection(): Promise<boolean> {
  try {
    const result = await executeQuery('SELECT 1 AS test');
    return result.rows.length > 0;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error('❌ Postgres connection test failed:', message);
    return false;
  }
}
