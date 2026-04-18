"""
Utility functions for Finance Analytics Dashboard
"""

import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def format_large_number(num):
    """Format large numbers with K, M, B suffixes"""
    if abs(num) >= 1_000_000_000:
        return f"${num / 1_000_000_000:.2f}B"
    elif abs(num) >= 1_000_000:
        return f"${num / 1_000_000:.2f}M"
    elif abs(num) >= 1_000:
        return f"${num / 1_000:.2f}K"
    else:
        return f"${num:.2f}"

def format_currency(value):
    """Format as currency"""
    return f"${value:,.2f}"

def format_percentage(value, decimals=2):
    """Format as percentage"""
    return f"{value:.{decimals}f}%"

def get_color_for_value(value):
    """Get color based on value (green for positive, red for negative)"""
    return "green" if value >= 0 else "red"

def get_date_range_label(days):
    """Get label for date range"""
    if days == 7:
        return "1 Week"
    elif days == 30:
        return "1 Month"
    elif days == 90:
        return "3 Months"
    elif days == 365:
        return "1 Year"
    else:
        return f"{days} Days"

def calculate_cagr(start_value, end_value, years):
    """Calculate Compound Annual Growth Rate"""
    if start_value <= 0 or years <= 0:
        return 0
    return ((end_value / start_value) ** (1 / years) - 1) * 100

def get_date_range(days):
    """Get start and end dates for a date range"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def round_to_cents(value):
    """Round value to nearest cent"""
    return round(value, 2)

def calculate_daily_returns(values):
    """Calculate daily returns from a series of values"""
    if len(values) < 2:
        return pd.Series([])
    return values.pct_change() * 100

def calculate_moving_average(series, window):
    """Calculate moving average"""
    return series.rolling(window=window).mean()

def create_performance_summary(performance_df, holding_period_days=365):
    """Create a performance summary"""
    if performance_df.empty:
        return {}
    
    start_value = performance_df['total_value'].iloc[-1]
    end_value = performance_df['total_value'].iloc[0]
    
    ytd_return = performance_df['ytd_return'].iloc[0] if len(performance_df) > 0 else 0
    total_return = performance_df['total_return'].iloc[0] if len(performance_df) > 0 else 0
    
    return {
        'period_return': ((end_value - start_value) / start_value * 100),
        'ytd_return': ytd_return,
        'total_return': total_return,
        'current_value': end_value,
        'start_value': start_value
    }

def format_dataframe_for_display(df, currency_cols=None, percent_cols=None):
    """Format dataframe for display"""
    df_display = df.copy()
    
    if currency_cols:
        for col in currency_cols:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(format_currency)
    
    if percent_cols:
        for col in percent_cols:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: format_percentage(x))
    
    return df_display

def get_metric_change(current, previous):
    """Get change between current and previous values"""
    if previous == 0:
        return 0
    return ((current - previous) / abs(previous)) * 100

def validate_date(date_str, date_format='%Y-%m-%d'):
    """Validate date string"""
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False
