/**
 * Database backend selector — oracle (default) or postgres via DB_BACKEND
 */

export { getDbBackend, isPostgresBackend, type DbBackend } from './backend';
export * as oracle from './oracle';
export * as postgres from './postgres';

import * as oracle from './oracle';
import * as postgres from './postgres';
import { getDbBackend } from './backend';

function activeModule() {
  return getDbBackend() === 'postgres' ? postgres : oracle;
}

export async function executeQuery<T = Record<string, unknown>>(
  query: string,
  binds?: Record<string, unknown>,
  options?: unknown,
  retries?: number
): Promise<{ rows: T[] }> {
  const mod = activeModule();
  if (getDbBackend() === 'postgres') {
    return mod.executeQuery<T>(query, binds as Record<string, unknown>);
  }
  return oracle.executeQuery<T>(query, binds, options, retries);
}

export async function initializePool(): Promise<void> {
  return activeModule().initializePool();
}

export async function closePool(): Promise<void> {
  return activeModule().closePool();
}

export async function testConnection(): Promise<boolean> {
  return activeModule().testConnection();
}
