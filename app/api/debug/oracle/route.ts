/**
 * Debug endpoint to check Oracle client initialization status
 * Temporary endpoint for troubleshooting
 */

import { NextResponse } from 'next/server';
import oracledb from 'oracledb';
import { initializeOracleClient } from '@/app/lib/db/oracle';

export async function GET() {
  try {
    // Try to initialize and catch any errors
    let initError = null;
    try {
      initializeOracleClient();
    } catch (err: any) {
      initError = {
        message: err.message,
        stack: err.stack,
      };
    }

    // Check thick mode
    let thickMode = false;
    let clientVersion = null;
    try {
      clientVersion = (oracledb as any).oracleClientVersionString;
      thickMode = !!clientVersion;
    } catch {
      thickMode = false;
    }

    // Try manual initialization to see what happens
    let manualInitError = null;
    let manualInitSuccess = false;
    if (!thickMode) {
      try {
        const fs = require('fs');
        const libDir = '/opt/oracle/instantclient_23_3';
        if (fs.existsSync(libDir)) {
          const walletPath = process.env.ADB_WALLET_PATH;
          oracledb.initOracleClient({ 
            libDir: libDir,
            configDir: walletPath 
          });
          manualInitSuccess = true;
          // Check again
          try {
            clientVersion = (oracledb as any).oracleClientVersionString;
            thickMode = !!clientVersion;
          } catch {}
        }
      } catch (err: any) {
        manualInitError = {
          message: err.message,
          code: (err as any).code,
          errorNum: (err as any).errorNum,
        };
      }
    }

    // Check library detection
    const fs = require('fs');
    const path = require('path');
    const possibleLibDirs = [
      '/opt/oracle/instantclient_23_3',
      '/opt/oracle/instantclient_21_1',
    ];

    const libDirs = possibleLibDirs.map(dir => {
      const exists = fs.existsSync(dir);
      let hasLib = false;
      if (exists) {
        const libFiles = ['libclntsh.dylib', 'libclntsh.so'];
        for (const libFile of libFiles) {
          const libPath = path.join(dir, libFile);
          if (fs.existsSync(libPath)) {
            hasLib = true;
            break;
          }
        }
      }
      return { dir, exists, hasLib };
    });

    return NextResponse.json({
      thickMode,
      clientVersion,
      initError,
      manualInit: {
        attempted: !thickMode,
        success: manualInitSuccess,
        error: manualInitError,
      },
      environment: {
        ADB_WALLET_PATH: process.env.ADB_WALLET_PATH || 'not set',
        TNS_ADMIN: process.env.TNS_ADMIN || 'not set',
        ADB_CONNECTION_STRING: process.env.ADB_CONNECTION_STRING ? 'set' : 'not set',
        ADB_USERNAME: process.env.ADB_USERNAME || 'not set',
        hasPassword: !!process.env.ADB_PASSWORD,
      },
      platform: {
        platform: process.platform,
        arch: process.arch,
      },
      libraryDirs: libDirs,
    });
  } catch (error: any) {
    return NextResponse.json({
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
    }, { status: 500 });
  }
}
