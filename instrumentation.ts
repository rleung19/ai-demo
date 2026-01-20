/**
 * Next.js Instrumentation Hook
 * 
 * This file runs code at server startup (before the server starts handling requests).
 * Used to initialize the Oracle connection pool early.
 * 
 * Requires Next.js 13+ (instrumentation hook is enabled by default in 16.1.1)
 */

// Module-level flag to prevent duplicate pool initialization
let poolInitializationStarted = false;

export async function register() {
  // Only run on server-side
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    console.log('[Instrumentation] Registering startup hooks...');
    
    // Check if pool already exists in global scope (prevents duplicate creation on module reload)
    if (typeof globalThis !== 'undefined' && globalThis.__oraclePool) {
      console.log('[Instrumentation] Pool already exists in global scope, skipping initialization');
      return;
    }
    
    // Check module-level flag (prevents duplicate calls if register() is called multiple times)
    if (poolInitializationStarted) {
      console.log('[Instrumentation] Pool initialization already started, skipping');
      return;
    }
    
    poolInitializationStarted = true;
    const { initializePool } = await import('./app/lib/db/oracle');
    
    // Initialize connection pool at startup (non-blocking)
    console.log('[Instrumentation] Calling initializePool()...');
    initializePool().catch((err) => {
      console.error('[Instrumentation] Failed to initialize pool at startup:', err.message);
      poolInitializationStarted = false; // Reset on error to allow retry
    });
  } else {
    console.log('[Instrumentation] Skipping (not server-side runtime)');
  }
}
