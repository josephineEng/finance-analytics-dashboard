# Finance Analytics Dashboard

A comprehensive financial analytics dashboard built with Python, SQL, and Streamlit. Designed to analyze investment portfolios, track performance metrics, and visualize financial trends.

## Features

- **Portfolio Overview**: Track total assets, returns, and performance metrics
- **Performance Analysis**: Visualize historical returns and asset allocation
- **Comparative Analytics**: Compare performance across different time periods
- **Detailed Reports**: View transaction history and individual holdings
- **Interactive Visualizations**: Dynamic charts and real-time metrics

## Tech Stack

- **Backend**: Python (Pandas, NumPy, SQLite)
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **Dashboard**: Streamlit
- **Data Processing**: Python scripts for ETL and data validation

## Project Structure

```
finance-analytics-dashboard/
├── data/
│   ├── sample_data.csv          # Sample financial data
│   └── init_database.sql        # Database initialization script
├── src/
│   ├── database.py              # Database connection and queries
│   ├── data_processor.py        # ETL and data processing
│   └── utils.py                 # Utility functions
├── dashboard.py                 # Main Streamlit dashboard
├── requirements.txt             # Python dependencies
├── .gitignore
└── README.md
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/finance-analytics-dashboard.git
cd finance-analytics-dashboard
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Initialize the database:

```bash
python src/database.py
```

## Usage

Run the dashboard:

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Key Metrics

- **Total Portfolio Value**: Real-time portfolio valuation
- **Year-to-Date Return**: YTD performance percentage
- **Total Return**: Cumulative return since inception
- **Daily Performance**: Day-over-day P&L
- **Asset Allocation**: Breakdown by asset class

## Data Schema

### Portfolios Table

- portfolio_id, name, creation_date, total_value

### Holdings Table

- holding_id, portfolio_id, symbol, quantity, purchase_price, current_price, sector

### Transactions Table

- transaction_id, portfolio_id, symbol, transaction_type, quantity, price, transaction_date

### Price History Table

- price_id, symbol, date, close_price, open_price, high, low, volume

## Future Enhancements

- [ ] Real-time data integration with financial APIs
- [ ] Risk analysis and portfolio optimization
- [ ] Backtesting functionality
- [ ] Machine learning models for price prediction
- [ ] Multi-user support with authentication
- [ ] Export reports to PDF
- [ ] Integration with tax calculation

## Author

Your Name

## License

MIT License - feel free to use this for your portfolio

## Contact

For questions or suggestions, reach out via email or LinkedIn.
