"""
Database module for Finance Analytics Dashboard
Handles database connections, initialization, and queries
"""

import sqlite3
import os
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

# Database path
DB_PATH = 'finance_analytics.db'

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initialize database with schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    schema_path = Path(__file__).parent.parent / 'data' / 'init_database.sql'
    
    with open(schema_path, 'r') as f:
        schema = f.read()
    
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def seed_sample_data():
    """Seed database with sample data for demonstration"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Create sample portfolio
        cursor.execute("""
            INSERT INTO portfolios (name, description, total_value) 
            VALUES (?, ?, ?)
        """, ('Growth Portfolio', 'Diversified growth portfolio', 250000))
        
        portfolio_id = cursor.lastrowid
        
        # Sample holdings data
        holdings_data = [
            (portfolio_id, 'AAPL', 100, 150.00, 185.50, 'Technology', 'Equity'),
            (portfolio_id, 'MSFT', 50, 300.00, 380.25, 'Technology', 'Equity'),
            (portfolio_id, 'JPM', 75, 120.00, 155.75, 'Financial Services', 'Equity'),
            (portfolio_id, 'JNJ', 40, 160.00, 158.50, 'Healthcare', 'Equity'),
            (portfolio_id, 'SPY', 200, 400.00, 455.30, 'Index', 'Equity'),
            (portfolio_id, 'BND', 150, 70.00, 72.45, 'Fixed Income', 'Bond'),
        ]
        
        for holding in holdings_data:
            cursor.execute("""
                INSERT INTO holdings (portfolio_id, symbol, quantity, purchase_price, 
                                    current_price, sector, asset_class)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, holding)
        
        # Sample transactions
        base_date = datetime.now()
        transactions_data = [
            (portfolio_id, 'AAPL', 'BUY', 100, 150.00, base_date - timedelta(days=180), 50),
            (portfolio_id, 'MSFT', 'BUY', 50, 300.00, base_date - timedelta(days=150), 50),
            (portfolio_id, 'JPM', 'BUY', 75, 120.00, base_date - timedelta(days=120), 75),
            (portfolio_id, 'JNJ', 'BUY', 40, 160.00, base_date - timedelta(days=90), 40),
            (portfolio_id, 'SPY', 'BUY', 200, 400.00, base_date - timedelta(days=60), 100),
            (portfolio_id, 'BND', 'BUY', 150, 70.00, base_date - timedelta(days=30), 50),
        ]
        
        for transaction in transactions_data:
            cursor.execute("""
                INSERT INTO transactions (portfolio_id, symbol, transaction_type, quantity, 
                                        price, transaction_date, commission)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, transaction)
        
        # Sample price history
        symbols = ['AAPL', 'MSFT', 'JPM', 'JNJ', 'SPY', 'BND']
        for symbol in symbols:
            for i in range(90):
                date = base_date - timedelta(days=i)
                price = 100 + (90 - i) + (i % 5)
                cursor.execute("""
                    INSERT OR IGNORE INTO price_history (symbol, date, open_price, 
                                                         high_price, low_price, close_price, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (symbol, date, price, price + 2, price - 1, price + 1, 1000000))
        
        # Sample performance metrics
        for i in range(90):
            date = base_date - timedelta(days=i)
            daily_return = -0.001 + (i % 2) * 0.0015
            cursor.execute("""
                INSERT INTO performance_metrics (portfolio_id, date, total_value, 
                                               daily_return, ytd_return, total_return)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (portfolio_id, date, 250000 + (90 - i) * 100, daily_return, 
                  0.15 + (i * 0.001), 0.35 + (i * 0.002)))
        
        conn.commit()
        print("Sample data seeded successfully")
        
    except sqlite3.IntegrityError as e:
        print(f"Data already exists: {e}")
    finally:
        conn.close()

# Query functions

def get_portfolio_overview(portfolio_id):
    """Get portfolio overview metrics"""
    conn = get_connection()
    query = """
        SELECT 
            p.portfolio_id,
            p.name,
            SUM(h.quantity * h.current_price) as total_value,
            COUNT(DISTINCT h.symbol) as holding_count
        FROM portfolios p
        LEFT JOIN holdings h ON p.portfolio_id = h.portfolio_id
        WHERE p.portfolio_id = ?
        GROUP BY p.portfolio_id
    """
    df = pd.read_sql_query(query, conn, params=[portfolio_id])
    conn.close()
    return df

def get_holdings(portfolio_id):
    """Get all holdings for a portfolio"""
    conn = get_connection()
    query = """
        SELECT 
            symbol,
            quantity,
            purchase_price,
            current_price,
            sector,
            asset_class,
            quantity * current_price as market_value,
            ((current_price - purchase_price) / purchase_price * 100) as return_percentage,
            (quantity * current_price) - (quantity * purchase_price) as unrealized_gain
        FROM holdings
        WHERE portfolio_id = ?
        ORDER BY market_value DESC
    """
    df = pd.read_sql_query(query, conn, params=[portfolio_id])
    conn.close()
    return df

def get_asset_allocation(portfolio_id):
    """Get asset allocation breakdown"""
    conn = get_connection()
    query = """
        SELECT 
            asset_class,
            SUM(quantity * current_price) as total_value,
            ROUND(SUM(quantity * current_price) * 100.0 / 
                  (SELECT SUM(quantity * current_price) FROM holdings WHERE portfolio_id = ?), 2) as percentage
        FROM holdings
        WHERE portfolio_id = ?
        GROUP BY asset_class
    """
    df = pd.read_sql_query(query, conn, params=[portfolio_id, portfolio_id])
    conn.close()
    return df

def get_performance_history(portfolio_id, days=90):
    """Get historical performance data"""
    conn = get_connection()
    query = """
        SELECT 
            date,
            total_value,
            daily_return,
            ytd_return,
            total_return
        FROM performance_metrics
        WHERE portfolio_id = ?
        AND date >= datetime('now', '-' || ? || ' days')
        ORDER BY date ASC
    """
    df = pd.read_sql_query(query, conn, params=[portfolio_id, days])
    df['date'] = pd.to_datetime(df['date'])
    conn.close()
    return df

def get_transaction_history(portfolio_id, limit=100):
    """Get transaction history"""
    conn = get_connection()
    query = """
        SELECT 
            symbol,
            transaction_type,
            quantity,
            price,
            commission,
            (quantity * price) as amount,
            transaction_date
        FROM transactions
        WHERE portfolio_id = ?
        ORDER BY transaction_date DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=[portfolio_id, limit])
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    conn.close()
    return df

def get_sector_performance(portfolio_id):
    """Get performance by sector"""
    conn = get_connection()
    query = """
        SELECT 
            sector,
            COUNT(*) as holding_count,
            SUM(quantity) as total_quantity,
            SUM(quantity * current_price) as total_value,
            SUM((quantity * current_price) - (quantity * purchase_price)) as unrealized_gain,
            ROUND(SUM((quantity * current_price) - (quantity * purchase_price)) * 100.0 / 
                  SUM(quantity * purchase_price), 2) as return_percentage
        FROM holdings
        WHERE portfolio_id = ?
        GROUP BY sector
        ORDER BY total_value DESC
    """
    df = pd.read_sql_query(query, conn, params=[portfolio_id])
    conn.close()
    return df

if __name__ == '__main__':
    # Initialize database and seed data
    if not os.path.exists(DB_PATH):
        initialize_database()
        seed_sample_data()
    else:
        print(f"Database already exists at {DB_PATH}")
