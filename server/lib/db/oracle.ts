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
  if (clientInitialized) {
    return;
  }

  const walletPath = process.env.ADB_WALLET_PATH;
  if (!walletPath) {
    console.warn('⚠️  ADB_WALLET_PATH not set, using thin mode (limited wallet support)');
    clientInitialized = true; // Mark as initialized to avoid repeated attempts
    return;
  }

  console.log(`[Oracle Init] Starting initialization with wallet: ${walletPath}`);

  // ALWAYS set TNS_ADMIN to wallet path (critical for wallet access)
  // This must be set BEFORE initOracleClient, matching test-node-connection.js
  process.env.TNS_ADMIN = walletPath;
  console.log(`[Oracle Init] Set TNS_ADMIN to: ${walletPath}`);

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

// DO NOT initialize on module load for Express server
// Initialization will happen lazily when getConnection() is called
// This ensures environment variables are loaded first

// Connection pool configuration - created lazily to ensure env vars are loaded
function getPoolConfig(): any {
  return {
    user: process.env.ADB_USERNAME || 'OML',
    password: process.env.ADB_PASSWORD,
    connectionString: process.env.ADB_CONNECTION_STRING,
    poolMin: 1, // Reduced to avoid too many idle connections
    poolMax: 5, // Reduced to avoid connection exhaustion
    poolIncrement: 1,
    poolTimeout: 30, // Reduced from 60 - close idle connections faster
    queueTimeout: 30000, // 30 seconds - reduced from 60
    enableStatistics: false,
    // Add connection validation
    stmtCacheSize: 0, // Disable statement cache to reduce memory
  };
}

let pool: any | null = null;
let poolRecreating = false;

/**
 * Check if pool is healthy
 */
async function isPoolHealthy(poolInstance: any): Promise<boolean> {
  let testConnection: any | null = null;
  try {
    testConnection = await poolInstance.getConnection();
    // Try a simple query to verify connection is alive
    await testConnection.execute('SELECT 1 FROM DUAL');
    return true;
  } catch (err: any) {
    // ORA-03113 means connection is broken
    if (err.message?.includes('ORA-03113') || err.message?.includes('end-of-file')) {
      return false;
    }
    return false;
  } finally {
    if (testConnection) {
      try {
        await testConnection.close();
      } catch {
        // Ignore close errors
      }
    }
  }
}

/**
 * Recreate the connection pool
 */
async function recreatePool(): Promise<any> {
  if (poolRecreating) {
    // Wait a bit and retry
    await new Promise(resolve => setTimeout(resolve, 1000));
    if (pool) {
      return pool;
    }
  }
  
  poolRecreating = true;
  
  try {
    // Close existing pool if it exists
    if (pool) {
      try {
        await pool.close(5); // Wait up to 5 seconds
      } catch {
        // Ignore errors when closing broken pool
      }
      pool = null;
    }
    
    // Wait a moment before recreating
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Recreate pool
    const config = getPoolConfig();
    pool = await oracledb.createPool(config);
    console.log('✓ Oracle connection pool recreated');
    return pool;
  } finally {
    poolRecreating = false;
  }
}

/**
 * Get or create connection pool
 */
export async function getPool(): Promise<any> {
  if (pool) {
    // Check if pool is healthy
    const healthy = await isPoolHealthy(pool);
    if (!healthy) {
      console.warn('⚠️  Pool is unhealthy, recreating...');
      return await recreatePool();
    }
    return pool;
  }

  if (!process.env.ADB_PASSWORD || !process.env.ADB_CONNECTION_STRING) {
    throw new Error('ADB_PASSWORD and ADB_CONNECTION_STRING must be set in environment variables');
  }

  // Ensure TNS_ADMIN is set BEFORE initializing Oracle client (critical!)
  const walletPath = process.env.ADB_WALLET_PATH;
  if (walletPath && !process.env.TNS_ADMIN) {
    process.env.TNS_ADMIN = walletPath;
    console.log(`[Pool] Set TNS_ADMIN to: ${walletPath}`);
  }

  try {
    // Ensure Oracle client is initialized before creating pool
    initializeOracleClient();
    
    // Get pool config (reads env vars at call time, not module load time)
    const config = getPoolConfig();
    pool = await oracledb.createPool(config);
    console.log('✓ Oracle connection pool created');
    return pool;
  } catch (err: any) {
    console.error('❌ Failed to create connection pool:', err.message);
    console.error('   Error code:', err.code);
    console.error('   Error number:', err.errorNum);
    throw new Error(`Database connection failed: ${err.message}`);
  }
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
 * Includes retry logic for ORA-03113 errors
 */
export async function getConnection(retries = 2): Promise<any> {
  // Ensure TNS_ADMIN is set BEFORE initializing Oracle client (critical!)
  // This matches the working test-node-connection.js pattern
  const walletPath = process.env.ADB_WALLET_PATH;
  if (walletPath && !process.env.TNS_ADMIN) {
    process.env.TNS_ADMIN = walletPath;
    console.log(`[Connection] Set TNS_ADMIN to: ${walletPath}`);
  }
  
  // Ensure Oracle client is initialized
  initializeOracleClient();
  
  if (!process.env.ADB_PASSWORD || !process.env.ADB_CONNECTION_STRING) {
    throw new Error('ADB_PASSWORD and ADB_CONNECTION_STRING must be set in environment variables');
  }

  // Get pool config to read connection string (reads env vars at call time)
  const config = getPoolConfig();
  const connectionString = config.connectionString;
  const thickMode = isThickMode();
  
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      // Try to use pool first
      const poolInstance = await getPool();
      const connection = await poolInstance.getConnection();
      
      // Validate connection is alive
      try {
        await connection.execute('SELECT 1 FROM DUAL');
        return connection;
      } catch (validateErr: any) {
        // Connection is broken, close it and retry
        try {
          await connection.close();
        } catch {
          // Ignore close errors
        }
        
        if (validateErr.message?.includes('ORA-03113') || validateErr.message?.includes('end-of-file')) {
          console.warn(`⚠️  Connection validation failed (ORA-03113), attempt ${attempt + 1}/${retries + 1}`);
          if (attempt < retries) {
            // Recreate pool and retry
            pool = null;
            await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1))); // Exponential backoff
            continue;
          }
        }
        throw validateErr;
      }
    } catch (poolErr: any) {
      // Check if it's an ORA-03113 error
      if (poolErr.message?.includes('ORA-03113') || poolErr.message?.includes('end-of-file')) {
        console.warn(`⚠️  Pool connection failed (ORA-03113), attempt ${attempt + 1}/${retries + 1}:`, poolErr.message);
        
        if (attempt < retries) {
          // Recreate pool and retry
          pool = null;
          await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1))); // Exponential backoff
          continue;
        }
      }
      
      // For other errors or final attempt, try direct connection
      if (attempt === retries) {
        console.warn('⚠️  Pool connection failed, trying direct connection:', poolErr.message);
        try {
          const connection = await oracledb.getConnection({
            user: config.user,
            password: config.password,
            connectionString: connectionString,
          });
          
          // Validate direct connection
          await connection.execute('SELECT 1 FROM DUAL');
          console.log('✓ Direct connection established');
          return connection;
        } catch (directErr: any) {
          console.error('❌ Direct connection failed:', directErr.message);
          console.error('   Connection string:', connectionString);
          console.error('   TNS_ADMIN:', process.env.TNS_ADMIN);
          console.error('   Wallet path:', walletPath);
          console.error('   Mode:', thickMode ? 'thick' : 'thin');
          
          // Provide helpful error message
          if (directErr.message.includes('ORA-12162')) {
            console.error('\n💡 ORA-12162: TNS alias not resolved');
            console.error('   Check:');
            console.error('   1. TNS_ADMIN is set correctly');
            console.error('   2. tnsnames.ora exists in wallet directory');
            console.error('   3. Connection string matches alias in tnsnames.ora');
          }
          
          throw new Error(`Database connection failed: ${directErr.message}`);
        }
      } else {
        // Retry with exponential backoff
        await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
        continue;
      }
    }
  }
  
  throw new Error('Failed to get connection after retries');
}

/**
 * Execute a query and return results
 * Includes retry logic for connection errors
 */
export async function executeQuery<T = any>(
  query: string,
  binds?: any,
  options?: any,
  retries = 1
): Promise<any> {
  let connection: any | null = null;
  
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      connection = await getConnection(attempt === retries ? 0 : 1); // Only retry connection on last attempt
      const executeOptions: any = {
        outFormat: oracledb.OUT_FORMAT_OBJECT,
        ...options,
      };
      
      // Always pass three parameters: query, binds (or {}), options
      // If binds is undefined, pass empty object to avoid parameter confusion
      const result = await connection.execute(
        query,
        binds || {},
        executeOptions
      );
      
      // Success - return result
      return result;
    } catch (err: any) {
      // Check if it's a connection error that we should retry
      const isConnectionError = 
        err.message?.includes('ORA-03113') ||
        err.message?.includes('end-of-file') ||
        err.message?.includes('connection') ||
        err.message?.includes('NJS-500');
      
      if (isConnectionError && attempt < retries) {
        console.warn(`⚠️  Query failed with connection error (attempt ${attempt + 1}/${retries + 1}), retrying...`);
        // Close broken connection
        if (connection) {
          try {
            await connection.close();
          } catch {
            // Ignore close errors
          }
          connection = null;
        }
        // Invalidate pool so it gets recreated
        if (pool) {
          pool = null;
        }
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
        continue;
      }
      
      // Not a retryable error or final attempt
      console.error('❌ Query execution failed:', err.message);
      console.error('   Error code:', err.code);
      console.error('   Error number:', err.errorNum);
      throw err;
    } finally {
      if (connection) {
        try {
          await connection.close();
        } catch (closeErr: any) {
          // Only log if it's not a connection error (which is expected for broken connections)
          if (!closeErr.message?.includes('ORA-03113') && !closeErr.message?.includes('end-of-file')) {
            console.warn('⚠️  Error closing connection:', closeErr.message);
          }
        }
        connection = null;
      }
    }
  }
  
  throw new Error('Query execution failed after retries');
}

/**
 * Initialize connection pool at startup
 * Call this when the server starts to warm up connections
 */
export async function initializePool(): Promise<void> {
  try {
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

    // Ensure TNS_ADMIN is set BEFORE initializing Oracle client (critical!)
    const walletPath = process.env.ADB_WALLET_PATH;
    if (walletPath && !process.env.TNS_ADMIN) {
      process.env.TNS_ADMIN = walletPath;
      console.log(`[Test Connection] Set TNS_ADMIN to: ${walletPath}`);
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
