// Minimal type declaration for the `oracledb` package to satisfy TypeScript.
// These are intentionally loose (mostly `any`) and cover only what this app uses.

declare module 'oracledb' {
  // Core opaque types
  export type PoolAttributes = any;
  export type Pool = any;
  export type Connection = any;
  export type ExecuteOptions = any;
  export type BindParameters = any;

  // Constants
  export const OUT_FORMAT_OBJECT: number;

  // Functions used in this project
  export function initOracleClient(config?: any): void;
  export function createPool(config: PoolAttributes): Promise<Pool>;
  export function getConnection(config: any): Promise<Connection>;

  // Default export (namespace-style)
  const oracledb: {
    OUT_FORMAT_OBJECT: number;
    initOracleClient: typeof initOracleClient;
    createPool: typeof createPool;
    getConnection: typeof getConnection;
  } & Record<string, any>;

  export default oracledb;
}

