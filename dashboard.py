"""
Finance Analytics Dashboard - Main Application
A comprehensive financial portfolio analytics dashboard built with Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.database import (
    initialize_database, seed_sample_data, 
    get_portfolio_overview, get_holdings, get_asset_allocation,
    get_performance_history, get_transaction_history, get_sector_performance
)
from src.data_processor import DataProcessor
from src.utils import (
    format_currency, format_percentage, format_large_number,
    get_date_range, calculate_cagr
)

# Page configuration
st.set_page_config(
    page_title="Finance Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .positive {
        color: #27AE60;
        font-weight: bold;
    }
    .negative {
        color: #E74C3C;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def initialize_app():
    """Initialize application"""
    import os
    if not os.path.exists('finance_analytics.db'):
        initialize_database()
        seed_sample_data()
        st.success("Database initialized with sample data!")

def render_metric_cards(portfolio_id):
    """Render key metric cards"""
    holdings = get_holdings(portfolio_id)
    performance = get_performance_history(portfolio_id, days=365)
    
    if holdings.empty:
        st.warning("No holdings data available")
        return
    
    metrics = DataProcessor.calculate_portfolio_metrics(holdings)
    perf_stats = DataProcessor.calculate_performance_stats(performance)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Portfolio Value",
            format_large_number(metrics['total_value']),
            f"{metrics['total_return_percentage']:.2f}%"
        )
    
    with col2:
        st.metric(
            "Total Return",
            format_currency(metrics['total_unrealized_gain']),
            f"{metrics['total_return_percentage']:.2f}%"
        )
    
    with col3:
        st.metric(
            "Sharpe Ratio",
            f"{perf_stats.get('sharpe_ratio', 0):.2f}",
            "Annual"
        )
    
    with col4:
        st.metric(
            "Max Drawdown",
            f"{perf_stats.get('max_drawdown', 0)*100:.2f}%",
            "Historical"
        )

def render_performance_chart(portfolio_id):
    """Render performance chart"""
    performance = get_performance_history(portfolio_id, days=90)
    
    if performance.empty:
        st.warning("No performance data available")
        return
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=performance['date'],
        y=performance['total_value'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#1f77b4', width=2),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    
    fig.update_layout(
        title="Portfolio Value Trend (90 Days)",
        xaxis_title="Date",
        yaxis_title="Value ($)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_allocation_charts(portfolio_id):
    """Render allocation charts"""
    holdings = get_holdings(portfolio_id)
    
    if holdings.empty:
        st.warning("No holdings data available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Asset allocation pie chart
        allocation = DataProcessor.calculate_allocation_weights(holdings)
        
        fig = go.Figure(data=[go.Pie(
            labels=allocation['asset_class'],
            values=allocation['value'],
            hole=0.3,
            text=allocation['weight'],
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>Value: $%{value:,.0f}<br>Weight: %{text:.1f}%<extra></extra>'
        )])
        
        fig.update_layout(
            title="Asset Allocation",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sector allocation pie chart
        sectors = get_sector_performance(portfolio_id)
        
        if not sectors.empty:
            fig = go.Figure(data=[go.Pie(
                labels=sectors['sector'],
                values=sectors['total_value'],
                hole=0.3,
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.0f}<extra></extra>'
            )])
            
            fig.update_layout(
                title="Sector Allocation",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)

def render_holdings_table(portfolio_id):
    """Render holdings table"""
    holdings = get_holdings(portfolio_id)
    
    if holdings.empty:
        st.warning("No holdings data available")
        return
    
    # Format for display
    display_df = holdings[['symbol', 'quantity', 'purchase_price', 'current_price', 
                           'market_value', 'unrealized_gain', 'return_percentage']].copy()
    
    display_df['purchase_price'] = display_df['purchase_price'].apply(format_currency)
    display_df['current_price'] = display_df['current_price'].apply(format_currency)
    display_df['market_value'] = display_df['market_value'].apply(format_currency)
    display_df['unrealized_gain'] = display_df['unrealized_gain'].apply(format_currency)
    display_df['return_percentage'] = display_df['return_percentage'].apply(lambda x: format_percentage(x))
    
    display_df.columns = ['Symbol', 'Quantity', 'Buy Price', 'Current Price', 
                          'Market Value', 'Unrealized Gain/Loss', 'Return %']
    
    st.dataframe(display_df, use_container_width=True)

def render_top_bottom_performers(portfolio_id):
    """Render top and bottom performers"""
    holdings = get_holdings(portfolio_id)
    
    if holdings.empty:
        st.warning("No holdings data available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Top Performers")
        top = DataProcessor.identify_top_performers(holdings, n=5)
        
        if not top.empty:
            top_display = top.copy()
            top_display['return_percentage'] = top_display['return_percentage'].apply(lambda x: format_percentage(x))
            top_display['market_value'] = top_display['market_value'].apply(format_currency)
            top_display['unrealized_gain'] = top_display['unrealized_gain'].apply(format_currency)
            top_display.columns = ['Symbol', 'Return %', 'Market Value', 'Gain/Loss']
            st.dataframe(top_display, use_container_width=True)
    
    with col2:
        st.subheader("📉 Bottom Performers")
        bottom = DataProcessor.identify_bottom_performers(holdings, n=5)
        
        if not bottom.empty:
            bottom_display = bottom.copy()
            bottom_display['return_percentage'] = bottom_display['return_percentage'].apply(lambda x: format_percentage(x))
            bottom_display['market_value'] = bottom_display['market_value'].apply(format_currency)
            bottom_display['unrealized_gain'] = bottom_display['unrealized_gain'].apply(format_currency)
            bottom_display.columns = ['Symbol', 'Return %', 'Market Value', 'Gain/Loss']
            st.dataframe(bottom_display, use_container_width=True)

def render_sector_analysis(portfolio_id):
    """Render sector performance analysis"""
    sectors = get_sector_performance(portfolio_id)
    
    if sectors.empty:
        st.warning("No sector data available")
        return
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=sectors['sector'],
            y=sectors['total_value'],
            name='Total Value',
            marker_color='lightblue'
        )
    ])
    
    fig.update_layout(
        title="Sector Performance",
        xaxis_title="Sector",
        yaxis_title="Total Value ($)",
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display sector table
    display_df = sectors[['sector', 'holding_count', 'total_value', 'unrealized_gain', 'return_percentage']].copy()
    display_df['total_value'] = display_df['total_value'].apply(format_currency)
    display_df['unrealized_gain'] = display_df['unrealized_gain'].apply(format_currency)
    display_df['return_percentage'] = display_df['return_percentage'].apply(lambda x: format_percentage(x))
    display_df.columns = ['Sector', 'Holdings', 'Total Value', 'Unrealized Gain/Loss', 'Return %']
    
    st.dataframe(display_df, use_container_width=True)

def render_transactions_table(portfolio_id):
    """Render recent transactions"""
    transactions = get_transaction_history(portfolio_id, limit=20)
    
    if transactions.empty:
        st.info("No transactions available")
        return
    
    display_df = transactions[['symbol', 'transaction_type', 'quantity', 'price', 
                               'amount', 'commission', 'transaction_date']].copy()
    
    display_df['price'] = display_df['price'].apply(format_currency)
    display_df['amount'] = display_df['amount'].apply(format_currency)
    display_df['commission'] = display_df['commission'].apply(format_currency)
    display_df['transaction_date'] = pd.to_datetime(display_df['transaction_date']).dt.strftime('%Y-%m-%d %H:%M')
    
    display_df.columns = ['Symbol', 'Type', 'Quantity', 'Price', 'Amount', 'Commission', 'Date']
    
    st.dataframe(display_df, use_container_width=True)

def main():
    """Main application"""
    st.title("📊 Finance Analytics Dashboard")
    st.markdown("Professional portfolio analysis and performance tracking")
    
    # Initialize
    initialize_app()
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select View",
        ["Dashboard", "Holdings", "Performance", "Sector Analysis", "Transactions"]
    )
    
    # Portfolio selector (in a real app, this would show multiple portfolios)
    portfolio_id = 1  # Default to first portfolio
    
    if page == "Dashboard":
        st.header("Portfolio Overview")
        render_metric_cards(portfolio_id)
        
        st.divider()
        
        render_performance_chart(portfolio_id)
        
        st.divider()
        
        st.subheader("Asset & Sector Allocation")
        render_allocation_charts(portfolio_id)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            render_top_bottom_performers(portfolio_id)
    
    elif page == "Holdings":
        st.header("Portfolio Holdings")
        render_holdings_table(portfolio_id)
    
    elif page == "Performance":
        st.header("Performance Analysis")
        
        time_period = st.selectbox(
            "Select Time Period",
            [7, 30, 90, 365],
            format_func=lambda x: {7: "1 Week", 30: "1 Month", 90: "3 Months", 365: "1 Year"}[x]
        )
        
        performance = get_performance_history(portfolio_id, days=time_period)
        
        if not performance.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                latest_value = performance['total_value'].iloc[0]
                st.metric("Current Value", format_currency(latest_value))
            
            with col2:
                ytd_return = performance['ytd_return'].iloc[0]
                st.metric("YTD Return", format_percentage(ytd_return))
            
            with col3:
                total_return = performance['total_return'].iloc[0]
                st.metric("Total Return", format_percentage(total_return))
            
            st.divider()
            render_performance_chart(portfolio_id)
    
    elif page == "Sector Analysis":
        st.header("Sector Performance Analysis")
        render_sector_analysis(portfolio_id)
    
    elif page == "Transactions":
        st.header("Transaction History")
        render_transactions_table(portfolio_id)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px; margin-top: 20px;'>
        <p>Finance Analytics Dashboard | Built with Streamlit, Python & SQL | Data as of today</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
