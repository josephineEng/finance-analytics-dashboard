"""
Data processing module for Finance Analytics Dashboard
Handles ETL operations and data transformations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3

class DataProcessor:
    """Process and transform financial data"""
    
    @staticmethod
    def calculate_portfolio_metrics(holdings_df):
        """Calculate key portfolio metrics from holdings"""
        if holdings_df.empty:
            return {}
        
        total_value = holdings_df['market_value'].sum()
        total_cost = (holdings_df['quantity'] * holdings_df['purchase_price']).sum()
        total_unrealized = holdings_df['unrealized_gain'].sum()
        
        total_return_pct = (total_unrealized / total_cost * 100) if total_cost > 0 else 0
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_unrealized_gain': total_unrealized,
            'total_return_percentage': total_return_pct
        }
    
    @staticmethod
    def calculate_performance_stats(performance_df):
        """Calculate performance statistics"""
        if performance_df.empty:
            return {}
        
        daily_returns = performance_df['daily_return'].dropna()
        
        return {
            'avg_daily_return': daily_returns.mean(),
            'daily_volatility': daily_returns.std(),
            'sharpe_ratio': DataProcessor.calculate_sharpe_ratio(daily_returns),
            'max_drawdown': DataProcessor.calculate_max_drawdown(performance_df['total_value']),
            'win_rate': (daily_returns > 0).sum() / len(daily_returns) if len(daily_returns) > 0 else 0
        }
    
    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.02/252):
        """Calculate Sharpe ratio"""
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - risk_free_rate
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
    
    @staticmethod
    def calculate_max_drawdown(values):
        """Calculate maximum drawdown"""
        if len(values) == 0:
            return 0
        
        cumulative_max = values.cummax()
        drawdown = (values - cumulative_max) / cumulative_max
        return drawdown.min()
    
    @staticmethod
    def calculate_allocation_weights(holdings_df):
        """Calculate asset allocation weights"""
        if holdings_df.empty:
            return pd.DataFrame()
        
        total_value = holdings_df['market_value'].sum()
        
        allocation = holdings_df.groupby('asset_class').agg({
            'market_value': 'sum'
        }).reset_index()
        
        allocation['weight'] = (allocation['market_value'] / total_value * 100).round(2)
        allocation.columns = ['asset_class', 'value', 'weight']
        
        return allocation
    
    @staticmethod
    def calculate_sector_weights(holdings_df):
        """Calculate sector weights"""
        if holdings_df.empty:
            return pd.DataFrame()
        
        total_value = holdings_df['market_value'].sum()
        
        sector = holdings_df.groupby('sector').agg({
            'market_value': 'sum'
        }).reset_index()
        
        sector['weight'] = (sector['market_value'] / total_value * 100).round(2)
        sector.columns = ['sector', 'value', 'weight']
        
        return sector.sort_values('value', ascending=False)
    
    @staticmethod
    def identify_top_performers(holdings_df, n=5):
        """Get top performing holdings"""
        if holdings_df.empty:
            return pd.DataFrame()
        
        return holdings_df.nlargest(n, 'return_percentage')[
            ['symbol', 'return_percentage', 'market_value', 'unrealized_gain']
        ]
    
    @staticmethod
    def identify_bottom_performers(holdings_df, n=5):
        """Get bottom performing holdings"""
        if holdings_df.empty:
            return pd.DataFrame()
        
        return holdings_df.nsmallest(n, 'return_percentage')[
            ['symbol', 'return_percentage', 'market_value', 'unrealized_gain']
        ]
    
    @staticmethod
    def format_currency(value):
        """Format value as currency"""
        return f"${value:,.2f}"
    
    @staticmethod
    def format_percentage(value):
        """Format value as percentage"""
        return f"{value:.2f}%"

class DataValidator:
    """Validate data integrity"""
    
    @staticmethod
    def validate_holdings(df):
        """Validate holdings data"""
        issues = []
        
        if df.empty:
            issues.append("Holdings dataframe is empty")
            return issues
        
        # Check for required columns
        required_cols = ['symbol', 'quantity', 'current_price']
        for col in required_cols:
            if col not in df.columns:
                issues.append(f"Missing required column: {col}")
        
        # Check for negative values
        if (df['quantity'] < 0).any():
            issues.append("Found negative quantity values")
        
        if (df['current_price'] < 0).any():
            issues.append("Found negative price values")
        
        return issues
    
    @staticmethod
    def validate_transactions(df):
        """Validate transaction data"""
        issues = []
        
        if df.empty:
            return issues  # Empty is OK for transactions
        
        # Check transaction types
        valid_types = ['BUY', 'SELL']
        if not df['transaction_type'].isin(valid_types).all():
            issues.append("Invalid transaction types found")
        
        # Check for negative values
        if (df['quantity'] < 0).any():
            issues.append("Found negative quantity in transactions")
        
        if (df['price'] < 0).any():
            issues.append("Found negative price in transactions")
        
        return issues
