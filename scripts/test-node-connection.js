/**
 * Test script to verify Node.js connection to Oracle ADB Serverless
 * Prerequisites:
 * - oracledb package installed (npm install oracledb)
 * - ADB wallet configured
 * - Environment variables set (.env file)
 */

const path = require('path');
const fs = require('fs');

// Find project root (parent of scripts directory)
const scriptDir = __dirname;
const projectRoot = path.dirname(scriptDir);
const envFile = path.join(projectRoot, '.env');

// Load environment variables from project root
if (fs.existsSync(envFile)) {
  require('dotenv').config({ path: envFile });
  console.log(`✓ Loaded .env file from: ${envFile}`);
} else {
  console.warn(`⚠️  WARNING: .env file not found at ${envFile}`);
  console.warn('   Copy .env.example to .env and configure it');
  // Try loading from current directory as fallback
  require('dotenv').config();
}

const oracledb = require('oracledb');

async function testConnection() {
  console.log('='.repeat(60));
  console.log('Testing Node.js Connection to Oracle ADB');
  console.log('='.repeat(60));
  
  // Check environment variables
  const walletPath = process.env.ADB_WALLET_PATH;
  const connectionString = process.env.ADB_CONNECTION_STRING;
  const username = process.env.ADB_USERNAME || 'OML';
  let password = process.env.ADB_PASSWORD;
  
  // Debug password loading (without showing actual password)
  if (password) {
    console.log(`✓ Password loaded (length: ${password.length}, ends with #: ${password.endsWith('#')})`);
  }
  
  if (!walletPath) {
    console.error('❌ ERROR: ADB_WALLET_PATH not set in environment');
    console.error('   Set it in .env file or export ADB_WALLET_PATH=/path/to/wallet');
    return false;
  }
  
  if (!connectionString) {
    console.error('❌ ERROR: ADB_CONNECTION_STRING not set in environment');
    return false;
  }
  
  if (!password) {
    console.error('❌ ERROR: ADB_PASSWORD not set in environment');
    return false;
  }
  
  console.log(`✓ Wallet path: ${walletPath}`);
  console.log(`✓ Connection string: ${connectionString}`);
  console.log(`✓ Username: ${username}`);
  
  // Set TNS_ADMIN environment variable (required for wallet access)
  process.env.TNS_ADMIN = walletPath;
  console.log(`✓ Set TNS_ADMIN to: ${walletPath}`);
  
  // Configure oracledb to use wallet and Instant Client
  // Try to find ARM64 Instant Client (same location as Python)
  const fs = require('fs');
  const possibleLibDirs = [
    '/opt/oracle/instantclient_23_3',
    '/opt/oracle/instantclient_21_1',
    '/opt/oracle/instantclient_21_2',
    '/opt/oracle/instantclient_21_3',
    '/opt/homebrew/lib',
  ];
  
  let libDir = null;
  for (const dir of possibleLibDirs) {
    if (fs.existsSync(dir)) {
      // Check if it contains libclntsh.dylib or libclntsh.so
      const libFiles = ['libclntsh.dylib', 'libclntsh.so'];
      for (const libFile of libFiles) {
        const libPath = require('path').join(dir, libFile);
        if (fs.existsSync(libPath) || fs.existsSync(libPath + '.19.1') || fs.existsSync(libPath + '.21.1')) {
          libDir = dir;
          break;
        }
      }
      if (libDir) break;
    }
  }
  
  try {
    if (libDir) {
      oracledb.initOracleClient({ 
        libDir: libDir,
        configDir: walletPath 
      });
      console.log(`✓ Oracle client initialized with libDir: ${libDir}`);
    } else {
      oracledb.initOracleClient({ configDir: walletPath });
      console.log(`✓ Oracle client initialized with wallet: ${walletPath}`);
      console.warn('⚠️  WARNING: Oracle Instant Client not found, using thin mode');
      console.warn('   Thin mode has limited ADB wallet support');
    }
  } catch (err) {
    if (err.message.includes('Oracle Client library')) {
      console.warn('⚠️  WARNING: Oracle Instant Client may not be installed');
      console.warn('   Connection may still work if wallet is properly configured');
      console.warn(`   Error: ${err.message}`);
    } else {
      console.warn(`⚠️  WARNING: ${err.message}`);
    }
  }
  
  let connection;
  
  try {
    // Attempt connection
    console.log('\nAttempting connection...');
    connection = await oracledb.getConnection({
      user: username,
      password: password,
      connectionString: connectionString,
    });
    
    console.log(`✓ Successfully connected to ADB as ${username}`);
    
    // Test a simple query
    const result = await connection.execute('SELECT 1 FROM DUAL');
    console.log(`✓ Test query successful: ${result.rows[0][0]}`);
    
    // Test OML schema access
    try {
      const omlResult = await connection.execute(
        'SELECT COUNT(*) FROM USER_TABLES'
      );
      console.log(`✓ Can query user tables: ${omlResult.rows[0][0]} tables`);
    } catch (err) {
      console.warn(`⚠️  Could not query user tables: ${err.message}`);
    }
    
    await connection.close();
    console.log('✓ Connection closed successfully');
    
    return true;
  } catch (err) {
    console.error(`❌ ERROR: Connection failed: ${err.message}`);
    console.error('\nTroubleshooting:');
    console.error('1. Verify wallet files are in ADB_WALLET_PATH');
    console.error('2. Check ADB_CONNECTION_STRING format: hostname:port/service_name');
    console.error('3. Verify ADB_USERNAME and ADB_PASSWORD are correct');
    console.error('4. Ensure Oracle Instant Client is installed');
    console.error('5. Check network connectivity to ADB');
    
    if (connection) {
      try {
        await connection.close();
      } catch (closeErr) {
        // Ignore close errors
      }
    }
    
    return false;
  }
}

async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('Oracle ADB Connection Test - Node.js');
  console.log('='.repeat(60));
  console.log('\nChecking prerequisites...\n');
  
  const success = await testConnection();
  
  console.log('\n' + '='.repeat(60));
  console.log('Test Summary');
  console.log('='.repeat(60));
  console.log(`oracledb:   ${success ? '✓ PASS' : '❌ FAIL'}`);
  
  if (success) {
    console.log('\n✓ Node.js connection test passed!');
    process.exit(0);
  } else {
    console.log('\n⚠️  Connection test failed. Review errors above.');
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
