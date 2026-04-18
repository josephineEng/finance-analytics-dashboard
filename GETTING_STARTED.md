# Getting Started

This guide will help you set up and run the Finance Analytics Dashboard on your local machine.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/finance-analytics-dashboard.git
cd finance-analytics-dashboard
```

### 2. Create Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
python src/database.py
```

This will:

- Create the SQLite database with the complete schema
- Populate it with sample financial data
- Set up all necessary tables and indexes

### 5. Run the Dashboard

```bash
streamlit run dashboard.py
```

The application will open in your default browser at `http://localhost:8501`

## Project Structure Explanation

```
finance-analytics-dashboard/
├── data/
│   ├── sample_data.csv          # Sample holdings data
│   └── init_database.sql        # Database schema
├── src/
│   ├── database.py              # Database operations & queries
│   ├── data_processor.py        # Data transformations & metrics
│   ├── utils.py                 # Helper functions
│   └── __init__.py              # Package initialization
├── dashboard.py                 # Main Streamlit app
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## Key Files Explained

### `src/database.py`

- Handles SQLite connections
- Provides functions to query portfolio data
- Includes seed data for demonstrations
- Contains queries for holdings, transactions, and performance metrics

### `src/data_processor.py`

- Calculates financial metrics (Sharpe ratio, max drawdown, etc.)
- Processes asset allocation
- Identifies top/bottom performers
- Validates data integrity

### `dashboard.py`

- Main Streamlit application
- Creates interactive visualizations
- Displays portfolio metrics and charts
- Multiple view tabs for different analyses

## Database Schema

The application uses SQLite with the following main tables:

- **portfolios**: Portfolio metadata
- **holdings**: Current security positions
- **transactions**: Buy/sell history
- **price_history**: Historical price data
- **performance_metrics**: Portfolio performance over time

## Customization

### Add Real Data

Replace sample data in `src/database.py` or modify `data/sample_data.csv`:

```python
# In src/database.py, modify seed_sample_data() function
```

### Connect to Real APIs

To use real market data, consider integrating:

- Alpha Vantage
- IEX Cloud
- Yahoo Finance API
- Polygon.io

### Upgrade to PostgreSQL

Change database connection in `src/database.py`:

```python
import psycopg2

DB_CONNECTION = "postgresql://user:password@localhost:5432/finance_db"
```

## Troubleshooting

### Port already in use

```bash
streamlit run dashboard.py --server.port 8502
```

### Database locked error

Delete `finance_analytics.db` and run:

```bash
python src/database.py
```

### Missing modules

```bash
pip install --upgrade -r requirements.txt
```

## Features Overview

### Dashboard Tab

- Portfolio overview with key metrics
- Performance trend chart
- Asset and sector allocation
- Top/bottom performers

### Holdings Tab

- Complete holdings list
- Current prices and unrealized gains
- Performance percentages

### Performance Tab

- Historical performance charts
- Selectable time periods
- Return metrics

### Sector Analysis Tab

- Sector-wise performance
- Holdings count by sector
- Comparative analysis

### Transactions Tab

- Recent transaction history
- Buy/sell details
- Transaction dates and amounts

## Next Steps

1. Add real market data via APIs
2. Implement user authentication
3. Add export to PDF functionality
4. Create watchlist features
5. Implement tax lot tracking
6. Add risk analysis tools

## Support

For issues or questions, please create an issue on GitHub or refer to the main README.md

## License

MIT License - see LICENSE file for details
