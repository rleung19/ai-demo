/**
 * Health Check Endpoint
 * Task 4.3: Create health check endpoint (GET /api/health)
 * 
 * Verifies database connectivity and returns service status
 */

import { NextResponse } from 'next/server';
import { testConnection } from '@/app/lib/db/oracle';

export async function GET() {
  try {
    // Check environment variables
    const envCheck = {
      hasWalletPath: !!process.env.ADB_WALLET_PATH,
      hasConnectionString: !!process.env.ADB_CONNECTION_STRING,
      hasUsername: !!process.env.ADB_USERNAME,
      hasPassword: !!process.env.ADB_PASSWORD,
    };

    // Test database connection with timeout
    let dbConnected = false;
    let dbError: string | null = null;
    
    try {
      // Set a 3-second timeout for database connection test
      const timeoutPromise = new Promise<boolean>((_, reject) => {
        setTimeout(() => reject(new Error('Database connection timeout')), 3000);
      });
      
      dbConnected = await Promise.race([
        testConnection(),
        timeoutPromise,
      ]) as boolean;
    } catch (error: any) {
      dbError = error.message || 'Database connection failed';
      console.warn('Database health check failed:', dbError);
    }

    const health = {
      status: dbConnected ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      services: {
        database: dbConnected ? 'connected' : 'disconnected',
      },
      environment: envCheck,
      ...(dbError && { databaseError: dbError }),
    };

    return NextResponse.json(health, {
      status: dbConnected ? 200 : 503,
    });
  } catch (error: any) {
    return NextResponse.json(
      {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: error.message,
        stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
      },
      { status: 503 }
    );
  }
}
