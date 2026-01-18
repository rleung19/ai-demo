# AI/ML Executive Dashboard

AI workshop demo project featuring a Next.js dashboard with 10 predictive KPIs, including churn risk analysis powered by Oracle Machine Learning on Oracle Autonomous Database Serverless.

## Features

- **10 Leading AI/ML KPIs** - Predictive indicators for B2C Fashion E-commerce
- **Churn Risk Analysis** - Real-time churn predictions from Oracle ADB
- **Interactive Dashboards** - Executive-focused visualizations
- **Oracle OML Integration** - Machine learning models trained in-database

## Getting Started

### Prerequisites

See [SETUP.md](SETUP.md) for complete setup instructions.

Quick start:
1. Install dependencies: `npm install` and `pip install -r requirements.txt`
2. Configure environment: Copy `.env.example` to `.env` and fill in ADB credentials
3. Set up ADB wallet: See [docs/ADB_SETUP.md](docs/ADB_SETUP.md)
4. Test connections: Run `python scripts/test-python-connection.py` and `node scripts/test-node-connection.js`

### Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

## Project Structure

```
├── app/                    # Next.js app directory
│   ├── components/        # React components
│   ├── data/             # Data sources (synthetic + API)
│   └── lib/              # Utilities and types
├── docs/                  # Documentation
│   └── ADB_SETUP.md      # Oracle ADB setup guide
├── oml-notebooks/         # OML notebook files
├── openspec/              # OpenSpec specifications
├── scripts/               # Utility scripts
│   ├── test-python-connection.py
│   └── test-node-connection.js
└── requirements.txt       # Python dependencies
```

## Documentation

- [Setup Guide](SETUP.md) - Quick setup instructions
- [ADB Setup Guide](docs/ADB_SETUP.md) - Detailed Oracle ADB configuration
- [OpenSpec Proposal](openspec/changes/add-churn-model-backend-api/proposal.md) - Churn model backend API proposal
- [OML Notebooks](oml-notebooks/README.md) - OML notebook documentation

## Technology Stack

- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Backend**: Next.js API Routes, Oracle ADB Serverless
- **ML**: Oracle Machine Learning (OML4Py), XGBoost
- **Database**: Oracle Autonomous Database Serverless

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Oracle ADB Documentation](https://docs.oracle.com/en/cloud/paas/autonomous-database/)
- [OML4Py Documentation](https://docs.oracle.com/en/database/oracle/machine-learning/oml4py/)
