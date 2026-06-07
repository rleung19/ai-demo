export type DbBackend = 'oracle' | 'postgres';

export function getDbBackend(): DbBackend {
  const value = (process.env.DB_BACKEND || 'oracle').toLowerCase();
  return value === 'postgres' ? 'postgres' : 'oracle';
}

export function isPostgresBackend(): boolean {
  return getDbBackend() === 'postgres';
}
