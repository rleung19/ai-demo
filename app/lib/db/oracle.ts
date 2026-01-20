/**
 * Oracle Database Connection Utility
 * Task 4.2: ADB connection utilities with connection pooling
 * 
 * Provides connection pooling and reusable database connection functions
 * for Next.js API routes.
 * 
 * Supports thick mode on macOS (Intel and ARM64) and Linux.
 */

import oracledb from 'oracledb';
import fs from 'fs';
import path from 'path';

// Initialize Oracle client (thick mode for wallet support)
let clientInitialized = false;

/**
 * Find Oracle Instant Client library directory
 * Checks for libclntsh.dylib (macOS) or libclntsh.so (Linux)
 */
function findOracleLibDir(): string | null {
  const possibleLibDirs = [
    '/opt/oracle/instantclient_23_3',
    '/opt/oracle/instantclient_21_1',
    '/opt/oracle/instantclient_21_2',
    '/opt/oracle/instantclient_21_3',
    process.env.ORACLE_CLIENT_LIB_DIR || '',
  ].filter(Boolean);

  // Library file names to check
  const libFiles = process.platform === 'darwin' 
    ? ['libclntsh.dylib', 'libclntsh.dylib.19.1', 'libclntsh.dylib.21.1', 'libclntsh.dylib.23.1']
    : ['libclntsh.so', 'libclntsh.so.19.1', 'libclntsh.so.21.1', 'libclntsh.so.23.1'];

  for (const dir of possibleLibDirs) {
    if (!fs.existsSync(dir)) continue;

    // Check if directory contains the library file
    for (const libFile of libFiles) {
      const libPath = path.join(dir, libFile);
      if (fs.existsSync(libPath)) {
        return dir;
      }
    }

    // Also check in lib subdirectory
    const libSubDir = path.join(dir, 'lib');
    if (fs.existsSync(libSubDir)) {
      for (const libFile of libFiles) {
        const libPath = path.join(libSubDir, libFile);
        if (fs.existsSync(libPath)) {
          return libSubDir;
        }
      }
    }
  }

  return null;
}

/**
 * Initialize Oracle client in thick mode
 * Must be called before any connection attempts
 */
export function initializeOracleClient(): void {
  // Early return if already initialized (no logging needed)
  if (clientInitialized) {
    return;
  }

  const walletPath = process.env.ADB_WALLET_PATH;
  if (!walletPath) {
    console.warn('⚠️  ADB_WALLET_PATH not set, using thin mode (limited wallet support)');
    clientInitialized = true; // Mark as initialized to avoid repeated attempts
    return;
  }

  // Only log if we're actually going to initialize
  console.log(`[Oracle Init] Starting initialization with wallet: ${walletPath}`);

  // Set TNS_ADMIN if not already set (critical for wallet access)
  if (!process.env.TNS_ADMIN) {
    process.env.TNS_ADMIN = walletPath;
  }

  try {
    const libDir = findOracleLibDir();

    if (libDir) {
      console.log(`[Oracle Init] Found library directory: ${libDir}`);
      // Try to initialize with both libDir and configDir (wallet)
      try {
        oracledb.initOracleClient({ 
          libDir: libDir,
          configDir: walletPath 
        });
        console.log(`✓ Oracle client initialized (thick mode): ${libDir}`);
        console.log(`   Wallet config: ${walletPath}`);
        // Verify thick mode is enabled
        try {
          const version = (oracledb as any).oracleClientVersionString;
          console.log(`   Client version: ${version}`);
        } catch {
          console.warn('   ⚠️  Could not verify client version');
        }
        clientInitialized = true;
        return;
      } catch (err: any) {
        // If already initialized, that's fine
        if (err.message && (err.message.includes('already been called') || err.message.includes('already initialized'))) {
          console.log('✓ Oracle client already initialized');
          clientInitialized = true;
          return;
        }
        
        // Check for NJS-045 (thick mode binary not available in Next.js)
        if (err.code === 'NJS-045' || err.message.includes('NJS-045')) {
          console.warn('⚠️  Thick mode not available (NJS-045) - using thin mode');
          console.warn('   This is expected in Next.js - thin mode will be used with TNS configuration');
          clientInitialized = true;
          return;
        }
        
        console.warn(`⚠️  First init attempt failed: ${err.message}`);
        
        // Try with just libDir (TNS_ADMIN env var should handle wallet)
        try {
          oracledb.initOracleClient({ libDir: libDir });
          console.log(`✓ Oracle client initialized (thick mode, libDir only): ${libDir}`);
          console.log(`   Using TNS_ADMIN: ${process.env.TNS_ADMIN}`);
          // Verify thick mode
          try {
            const version = (oracledb as any).oracleClientVersionString;
            console.log(`   Client version: ${version}`);
          } catch {
            console.warn('   ⚠️  Could not verify client version');
          }
          clientInitialized = true;
          return;
        } catch (err2: any) {
          if (err2.message && (err2.message.includes('already been called') || err2.message.includes('already initialized'))) {
            console.log('✓ Oracle client already initialized');
            clientInitialized = true;
            return;
          }
          
          // Check for NJS-045 again
          if (err2.code === 'NJS-045' || err2.message.includes('NJS-045')) {
            console.warn('⚠️  Thick mode not available (NJS-045) - using thin mode');
            clientInitialized = true;
            return;
          }
          
          console.warn(`⚠️  Could not initialize with libDir: ${err2.message}`);
          // Continue to thin mode fallback
        }
      }
    }

    // Fallback: try with just configDir (wallet) - this will also fail in Next.js but we try anyway
    try {
      oracledb.initOracleClient({ configDir: walletPath });
      console.log('✓ Oracle client initialized (thick mode, wallet only)');
      clientInitialized = true;
    } catch (err: any) {
      if (err.message && err.message.includes('already been called')) {
        console.log('✓ Oracle client already initialized');
        clientInitialized = true;
        return;
      }
      
      // NJS-045 means thick mode not available - this is expected in Next.js
      if (err.code === 'NJS-045' || err.message.includes('NJS-045')) {
        console.log('✓ Using thin mode (TNS_ADMIN configured for wallet access)');
        clientInitialized = true;
        return;
      }
      
      console.warn(`⚠️  Could not initialize Oracle client: ${err.message}`);
      console.log('✓ Falling back to thin mode (TNS_ADMIN configured)');
      clientInitialized = true;
    }
  } catch (err: any) {
    // NJS-045 is expected in Next.js - not an error
    if (err.code === 'NJS-045' || err.message.includes('NJS-045')) {
      console.log('✓ Using thin mode (TNS_ADMIN configured for wallet access)');
    } else {
      console.warn(`⚠️  Oracle client initialization error: ${err.message}`);
      console.log('✓ Using thin mode (TNS_ADMIN configured)');
    }
    clientInitialized = true;
  }
}

// Initialize on module load (critical for Next.js)
// Note: Thick mode may not work in Next.js dev mode due to path resolution issues
// Fallback to thin mode is handled automatically
if (typeof window === 'undefined') {
  // Server-side only
  // Try to initialize, but don't fail if it doesn't work (thin mode fallback)
  try {
    if (process.env.ADB_WALLET_PATH) {
      initializeOracleClient();
    }
  } catch (err: any) {
    console.warn('⚠️  Oracle client initialization skipped, will use thin mode:', err.message);
  }
}

// Connection pool configuration (typed as any to avoid hard dependency on oracledb TS types)
const poolConfig: any = {
  user: process.env.ADB_USERNAME || 'OML',
  password: process.env.ADB_PASSWORD,
  connectionString: process.env.ADB_CONNECTION_STRING,
  poolMin: 2,
  poolMax: 10,
  poolIncrement: 1,
  poolTimeout: 60,
  queueTimeout: 60000, // 60 seconds
  enableStatistics: false,
};

// Use global variable to persist across module reloads in Next.js
// In Node.js, globalThis persists across module reloads
declare global {
  var __oraclePool: any | null | undefined;
  var __oraclePoolPromise: Promise<any> | null | undefined;
}

// Use global variables that persist across Next.js module reloads
const getGlobalPool = (): any | null => {
  if (typeof globalThis !== 'undefined') {
    return globalThis.__oraclePool || null;
  }
  return null;
};

const setGlobalPool = (newPool: any | null): void => {
  if (typeof globalThis !== 'undefined') {
    globalThis.__oraclePool = newPool;
  }
};

const getGlobalPoolPromise = (): Promise<any> | null => {
  if (typeof globalThis !== 'undefined') {
    return globalThis.__oraclePoolPromise || null;
  }
  return null;
};

const setGlobalPoolPromise = (promise: Promise<any> | null): void => {
  if (typeof globalThis !== 'undefined') {
    globalThis.__oraclePoolPromise = promise;
  }
};

// Legacy module-level variables (for backward compatibility)
let pool: any | null = null;
let poolCreationPromise: Promise<any> | null = null;

/**
 * Get or create connection pool (singleton pattern with race condition protection)
 */
export async function getPool(): Promise<any> {
  // Check module-level pool first (fast path)
  if (pool) {
    return pool;
  }
  
  // Check global pool (persists across module reloads in Next.js)
  // Only check if module-level pool is null (indicates module was reloaded)
  const globalPool = getGlobalPool();
  if (globalPool) {
    pool = globalPool; // Sync module-level variable for faster future access
    // Only log once when we recover from a module reload
    console.log('[Pool] Recovered pool from global scope (module was reloaded)');
    return globalPool;
  }
  
  // Check global promise (persists across module reloads)
  const globalPromise = getGlobalPoolPromise();
  if (globalPromise) {
    poolCreationPromise = globalPromise; // Sync module-level variable
    console.log('[Pool] Waiting for existing pool creation (from global promise)...');
    try {
      const existingPool = await globalPromise;
      if (existingPool) {
        pool = existingPool;
        setGlobalPool(existingPool);
        console.log('[Pool] Pool set from global promise result');
        setGlobalPoolPromise(null);
        poolCreationPromise = null;
        return pool;
      }
    } catch (err) {
      setGlobalPoolPromise(null);
      poolCreationPromise = null;
      throw err;
    }
  }
  
  if (!process.env.ADB_PASSWORD || !process.env.ADB_CONNECTION_STRING) {
    throw new Error('ADB_PASSWORD and ADB_CONNECTION_STRING must be set in environment variables');
  }

  // ATOMIC ACQUISITION: Check global promise one more time (double-check pattern)
  // Another module instance might have created it between our first check and now
  const finalGlobalPromise = getGlobalPoolPromise();
  if (finalGlobalPromise) {
    poolCreationPromise = finalGlobalPromise; // Sync module-level
    console.log('[Pool] Global promise appeared during check, waiting for it...');
    try {
      const existingPool = await finalGlobalPromise;
      if (existingPool) {
        pool = existingPool;
        setGlobalPool(existingPool);
        console.log('[Pool] Pool set from final global promise check');
        return pool;
      }
    } catch (err) {
      throw err;
    }
  }

  // Create a promise for pool creation (acts as a lock)
  // CRITICAL: Set global promise IMMEDIATELY (synchronously) before any async work
  // This prevents race conditions where multiple module instances all try to create a pool
  console.log('[Pool] Starting pool creation...');
  poolCreationPromise = (async () => {
    try {
      // Triple-check global pool (another instance might have created it)
      const existingGlobalPool = getGlobalPool();
      if (existingGlobalPool) {
        pool = existingGlobalPool;
        console.log('[Pool] Found existing pool in global scope (triple-check), returning it');
        poolCreationPromise = null;
        setGlobalPoolPromise(null);
        return pool;
      }

      // Triple-check module-level pool
      if (pool) {
        setGlobalPool(pool);
        console.log('[Pool] Pool already exists (triple-check), returning existing pool');
        poolCreationPromise = null;
        setGlobalPoolPromise(null);
        return pool;
      }

      // Ensure Oracle client is initialized before creating pool
      initializeOracleClient();
      
      const newPool = await oracledb.createPool(poolConfig);
      // Set pool in BOTH global and module-level variables (critical for Next.js module reloads)
      pool = newPool;
      setGlobalPool(newPool);
      console.log('✓ Oracle connection pool created');
      console.log('[Pool] Pool set in both global and module scope');
      // Clear global promise now that pool is created (so new module instances use the pool directly)
      setGlobalPoolPromise(null);
      poolCreationPromise = null;
      return pool;
    } catch (err: any) {
      console.error('❌ Failed to create connection pool:', err.message);
      console.error('   Error code:', err.code);
      console.error('   Error number:', err.errorNum);
      // Clear BOTH global and module promises on error so retry is possible
      setGlobalPoolPromise(null);
      poolCreationPromise = null;
      throw new Error(`Database connection failed: ${err.message}`);
    }
  })();

  // CRITICAL: Store promise in global scope IMMEDIATELY (synchronously)
  // This must happen BEFORE the async function starts executing
  // Once stored, all other module instances will see it and wait for this one
  setGlobalPoolPromise(poolCreationPromise);
  console.log('[Pool] Promise stored in global scope (lock acquired)');

  return poolCreationPromise;
}

/**
 * Check if Oracle client is in thick mode
 */
function isThickMode(): boolean {
  try {
    // Check if thick mode is enabled by checking for client version
    // In thick mode, this will return a version string
    const version = (oracledb as any).oracleClientVersionString;
    return !!version;
  } catch {
    return false;
  }
}

/**
 * Ensure TNS configuration is set up for thin mode
 */
function ensureTNSConfig(): void {
  const walletPath = process.env.ADB_WALLET_PATH;
  if (walletPath && !process.env.TNS_ADMIN) {
    process.env.TNS_ADMIN = walletPath;
  }
}

/**
 * Get a connection from the pool (or create direct connection if pool fails)
 */
export async function getConnection(): Promise<any> {
  // Ensure Oracle client is initialized
  initializeOracleClient();
  
  // Ensure TNS configuration is set (critical for thin mode wallet access)
  ensureTNSConfig();
  
  const thickMode = isThickMode();
  if (!thickMode) {
    console.log('ℹ️  Using thin mode (TNS_ADMIN configured for wallet access)');
  }
  
  if (!process.env.ADB_PASSWORD || !process.env.ADB_CONNECTION_STRING) {
    throw new Error('ADB_PASSWORD and ADB_CONNECTION_STRING must be set in environment variables');
  }

  // In thin mode, ensure we're using TNS alias format
  const connectionString = poolConfig.connectionString;
  const walletPath = process.env.ADB_WALLET_PATH;
  
  try {
    // Try to use pool first
    const poolInstance = await getPool();
    return await poolInstance.getConnection();
  } catch (poolErr: any) {
    console.warn('⚠️  Pool connection failed, trying direct connection:', poolErr.message);
    // Fallback to direct connection
    try {
      const connection = await oracledb.getConnection({
        user: poolConfig.user,
        password: poolConfig.password,
        connectionString: connectionString,
      });
      console.log('✓ Direct connection established');
      return connection;
    } catch (directErr: any) {
      console.error('❌ Direct connection failed:', directErr.message);
      console.error('   Connection string:', connectionString);
      console.error('   TNS_ADMIN:', process.env.TNS_ADMIN);
      console.error('   Wallet path:', walletPath);
      console.error('   Mode:', thickMode ? 'thick' : 'thin');
      
      // Provide helpful error message
      if (!thickMode && directErr.message.includes('ORA-12506')) {
        console.error('\n💡 Tip: Thin mode may have limited wallet support.');
        console.error('   Ensure TNS_ADMIN is set and connection string uses TNS alias format.');
      }
      
      throw new Error(`Database connection failed: ${directErr.message}`);
    }
  }
}

/**
 * Execute a query and return results
 */
export async function executeQuery<T = any>(
  query: string,
  binds?: any,
  options?: any
): Promise<any> {
  let connection: any | null = null;
  try {
    connection = await getConnection();
    const executeOptions: any = {
      outFormat: oracledb.OUT_FORMAT_OBJECT,
      ...options,
    };

    // Always pass three parameters: query, binds (or {}), options
    // If binds is undefined, pass empty object to avoid parameter confusion (NJS-005)
    const result = await connection.execute(
      query,
      binds || {},
      executeOptions
    );
    return result;
  } catch (err: any) {
    console.error('❌ Query execution failed:', err.message);
    console.error('   Error code:', err.code);
    console.error('   Error number:', err.errorNum);
    throw err;
  } finally {
    if (connection) {
      try {
        await connection.close();
      } catch (closeErr: any) {
        console.warn('⚠️  Error closing connection:', closeErr.message);
      }
    }
  }
}

/**
 * Initialize connection pool at startup
 * Call this when the server starts to warm up connections
 */
export async function initializePool(): Promise<void> {
  try {
    // Check if pool already exists in global scope (prevents duplicate creation)
    const existingPool = getGlobalPool();
    if (existingPool) {
      console.log('[Pool Init] Pool already exists in global scope, skipping initialization');
      // Sync module-level variable
      pool = existingPool;
      return;
    }
    
    console.log('[Pool Init] Initializing connection pool at startup...');
    await getPool();
    console.log('✓ Connection pool initialized and ready');
  } catch (err: any) {
    console.error('❌ Failed to initialize connection pool at startup:', err.message);
    console.warn('⚠️  Pool will be created lazily on first request');
    // Don't throw - allow server to start, pool will be created on first request
  }
}

/**
 * Close the connection pool (call on app shutdown)
 */
export async function closePool(): Promise<void> {
  if (pool) {
    try {
      await pool.close(10); // Wait up to 10 seconds
      pool = null;
      console.log('✓ Oracle connection pool closed');
    } catch (err: any) {
      console.error('❌ Error closing connection pool:', err.message);
    }
  }
}

/**
 * Test database connection
 */
export async function testConnection(): Promise<boolean> {
  try {
    // Check if environment variables are set
    if (!process.env.ADB_PASSWORD || !process.env.ADB_CONNECTION_STRING) {
      console.error('❌ Missing environment variables:', {
        hasPassword: !!process.env.ADB_PASSWORD,
        hasConnectionString: !!process.env.ADB_CONNECTION_STRING,
        hasWalletPath: !!process.env.ADB_WALLET_PATH,
      });
      return false;
    }

    // Ensure Oracle client is initialized
    initializeOracleClient();

    const result = await executeQuery('SELECT 1 AS test FROM DUAL');
    return result.rows && result.rows.length > 0;
  } catch (err: any) {
    console.error('❌ Connection test failed:', err.message);
    console.error('   Error details:', {
      code: err.code,
      errorNum: err.errorNum,
      message: err.message,
    });
    return false;
  }
}
