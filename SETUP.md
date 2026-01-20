# Setup Guide - Churn Model Backend API

This guide provides step-by-step instructions for setting up the prerequisites for the churn model backend API.

## Quick Start

1. **Set up environment variables** (5 minutes)
2. **Install dependencies** (10 minutes)
3. **Configure ADB wallet** (15 minutes)
4. **Test connections** (5 minutes)

**Total time: ~35 minutes**

## Prerequisites Checklist

- [ ] Oracle Cloud account with ADB Serverless access
- [ ] ADB instance created with OML enabled
- [ ] ADB wallet downloaded
- [ ] Python 3.8+ installed
- [ ] Node.js 18+ installed
- [ ] Oracle Instant Client installed (for local development)

## Step-by-Step Setup

### 1. Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your ADB credentials
# See docs/ADB_SETUP.md for detailed instructions
```

Required variables:
- `ADB_WALLET_PATH` - Path to wallet directory
- `ADB_CONNECTION_STRING` - ADB connection string
- `ADB_USERNAME` - OML schema username
- `ADB_PASSWORD` - OML schema password

### 2. Install Python Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Note: OML4Py requires Oracle Machine Learning client
# See docs/ADB_SETUP.md for OML4Py installation
```

### 3. Install Node.js Dependencies

```bash
# Install Node.js packages
npm install

# This will install oracledb for database connections
```

### 4. Configure ADB Wallet

See [docs/ADB_SETUP.md](docs/ADB_SETUP.md) for detailed wallet setup instructions.

Quick steps:
1. Download wallet from Oracle Cloud Console
2. Extract to a secure directory
3. Update `.env` with wallet path
4. Set `TNS_ADMIN` to wallet directory

### 5. Test Connections

```bash
# Test Python connection (OML4Py and oracledb)
python scripts/test-python-connection.py

# Test Node.js connection
node scripts/test-node-connection.js
```

Both should show ✓ PASS for all tests.

### 6. Verify OML Schema

Connect to ADB and verify OML schema exists:

```sql
-- Connect as ADMIN
SELECT username FROM all_users WHERE username = 'OML';

-- If OML doesn't exist, create it (see docs/ADB_SETUP.md)
```

## Verification

After setup, verify:

- [ ] `.env` file configured with ADB credentials
- [ ] Python test script passes
- [ ] Node.js test script passes
- [ ] OML schema exists and is accessible
- [ ] Can query database from both Python and Node.js

## Troubleshooting

See [docs/ADB_SETUP.md](docs/ADB_SETUP.md) for detailed troubleshooting guide.

Common issues:
- **Connection errors**: Check wallet path and connection string
- **Missing Oracle Client**: Install Oracle Instant Client
- **OML4Py not found**: Install Oracle Machine Learning client
- **Permission errors**: Verify OML user has necessary privileges

## Next Steps

Once prerequisites are complete:

1. ✅ Proceed to **Architecture & Design** (Section 1)
2. ✅ Start **Dataset Acquisition** (Section 2)
3. ✅ Begin **ML Pipeline Development** (Section 3)

## Additional Resources

- [ADB Setup Guide](docs/ADB_SETUP.md) - Detailed ADB configuration
- [OpenSpec Proposal](openspec/changes/add-churn-model-backend-api/proposal.md) - Project overview
- [Tasks Checklist](openspec/changes/add-churn-model-backend-api/tasks.md) - Implementation tasks
