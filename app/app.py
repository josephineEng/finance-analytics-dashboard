from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
from datetime import datetime
import os
from data_loader import get_data

# Get the project root directory (parent of the app directory)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Global variables - will be loaded lazily
customer_df = None
transactions_df = None

def get_customer_data():
    """Lazy load customer data"""
    global customer_df
    if customer_df is None:
        customer_df, transactions_df = get_data()
    return customer_df

def get_transaction_data():
    """Lazy load transaction data"""
    global transactions_df
    if transactions_df is None:
        customer_df, transactions_df = get_data()
    return transactions_df

@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('dashboard.html')

@app.route('/health')
def health_check():
    """Health check endpoint for debugging"""
    return jsonify({
        'status': 'healthy',
        'data_loaded': len(get_customer_data()) > 0,
        'customer_count': len(get_customer_data()),
        'transaction_count': len(get_transaction_data())
    })

@app.route('/api/dashboard-summary')
def dashboard_summary():
    """Get dashboard summary metrics"""
    df = get_customer_data()
    if df is None or len(df) == 0:
        return jsonify({'error': 'Data not loaded'}), 500
    
    summary = {
        'total_customers': len(df),
        'avg_satisfaction': round(df['satisfaction_score'].mean(), 2),
        'avg_nps': round(df['nps_score'].mean(), 2),
        'avg_clv': round(df['customer_lifetime_value'].mean(), 2),
        'churn_risk_customers': len(df[df['churn_probability'] > 0.5]),
        'avg_income': df['income_bracket'].value_counts().to_dict() if 'income_bracket' in df.columns else {}
    }
    return jsonify(summary)

@app.route('/api/customers')
def get_customers():
    """Get customers with optional filtering"""
    df = get_customer_data()
    if df is None or len(df) == 0:
        return jsonify({'error': 'Data not loaded'}), 500
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    segment = request.args.get('segment', None)
    
    df = df.copy()
    
    # Filter by segment if provided
    if segment and 'customer_segment' in df.columns:
        df = df[df['customer_segment'] == segment]
    
    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    
    customers = df.iloc[start:end].to_dict('records')
    return jsonify({
        'customers': customers,
        'total': len(df),
        'page': page,
        'per_page': per_page
    })

@app.route('/api/analytics/segments')
def segment_analytics():
    """Get customer segmentation analytics"""
    df = get_customer_data()
    if df is None or len(df) == 0:
        return jsonify({'error': 'Data not loaded'}), 500
    
    segments = df['customer_segment'].value_counts().to_dict()
    segment_stats = {}
    
    for segment in df['customer_segment'].unique():
        segment_data = df[df['customer_segment'] == segment]
        segment_stats[segment] = {
            'count': len(segment_data),
            'avg_satisfaction': round(segment_data['satisfaction_score'].mean(), 2),
            'avg_clv': round(segment_data['customer_lifetime_value'].mean(), 2),
            'avg_nps': round(segment_data['nps_score'].mean(), 2),
            'churn_risk': len(segment_data[segment_data['churn_probability'] > 0.5])
        }
    
    return jsonify(segment_stats)

@app.route('/api/analytics/income')
def income_analytics():
    """Get income bracket analytics"""
    if customer_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    income_stats = customer_df.groupby('income_bracket').agg({
        'customer_lifetime_value': ['count', 'mean', 'sum'],
        'satisfaction_score': 'mean',
        'nps_score': 'mean'
    }).to_dict()
    
    return jsonify(income_stats)

@app.route('/api/analytics/locations')
def location_analytics():
    """Get top locations"""
    if customer_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    top_locations = customer_df['location'].value_counts().head(10).to_dict()
    return jsonify(top_locations)

@app.route('/api/analytics/nps')
def nps_analytics():
    """Get NPS distribution"""
    if customer_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    nps_bins = [-100, -1, 0, 6, 8, 10]
    nps_labels = ['Detractors (<0)', 'Passive (0-6)', 'Promoters (7-10)']
    df = get_customer_data()
    if df is None or len(df) == 0:
        return jsonify({'error': 'Data not loaded'}), 500
    
    nps_dist = pd.cut(df['nps_score'], bins=nps_bins, labels=['Detractors', 'Passive', 'Promoters']).value_counts().to_dict()
    
    return jsonify(nps_dist)

@app.route('/api/analytics/churn')
def churn_analytics():
    """Get churn risk analytics"""
    df = get_customer_data()
    if df is None or len(df) == 0:
        return jsonify({'error': 'Data not loaded'}), 500
    
    high_risk = len(df[df['churn_probability'] > 0.7])
    medium_risk = len(df[(df['churn_probability'] > 0.4) & (df['churn_probability'] <= 0.7)])
    low_risk = len(df[df['churn_probability'] <= 0.4])
    
    return jsonify({
        'high_risk': high_risk,
        'medium_risk': medium_risk,
        'low_risk': low_risk,
        'total': len(df)
    })

@app.route('/api/analytics/demographics')
def demographics_analytics():
    """Get demographic analytics"""
    df = get_customer_data()
    if df is None or len(df) == 0:
        return jsonify({'error': 'Data not loaded'}), 500
    
    return jsonify({
        'gender': df['gender'].value_counts().to_dict(),
        'education': df['education_level'].value_counts().to_dict(),
        'marital_status': df['marital_status'].value_counts().to_dict(),
        'age_stats': {
            'mean': round(df['age'].mean(), 2),
            'median': float(df['age'].median()),
            'min': int(df['age'].min()),
            'max': int(df['age'].max())
        }
    })

@app.route('/api/analytics/transactions-summary')
def transactions_summary():
    """Get transaction summary metrics"""
    df = get_transaction_data()
    if df is None or len(df) == 0:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        summary = {
            'total_transactions': len(df),
            'total_volume': float(df['amount'].sum()) if 'amount' in df.columns else 0,
            'avg_transaction': float(df['amount'].mean()) if 'amount' in df.columns else 0,
            'max_transaction': float(df['amount'].max()) if 'amount' in df.columns else 0,
            'min_transaction': float(df['amount'].min()) if 'amount' in df.columns else 0,
        }
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/transaction-types')
def transaction_types():
    """Get transaction type distribution"""
    if transactions_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        if 'type' in transactions_df.columns:
            type_dist = transactions_df['type'].value_counts().to_dict()
        else:
            type_dist = {}
        
        return jsonify(type_dist)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/transaction-type-summary')
def transaction_type_summary():
    """Get detailed transaction type summary with volume and averages"""
    if transactions_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        summary = []
        total_volume = transactions_df['amount'].sum()
        total_count = len(transactions_df)
        
        if 'type' in transactions_df.columns:
            for txn_type in transactions_df['type'].unique():
                type_data = transactions_df[transactions_df['type'] == txn_type]
                count = len(type_data)
                volume = type_data['amount'].sum()
                avg_amount = type_data['amount'].mean()
                
                summary.append({
                    'type': txn_type,
                    'count': int(count),
                    'volume': float(volume),
                    'avg_amount': float(avg_amount),
                    'percentage': round((count / total_count) * 100, 2),
                    'volume_percentage': round((volume / total_volume) * 100, 2)
                })
        
        # Sort by count descending
        summary = sorted(summary, key=lambda x: x['count'], reverse=True)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/transaction-status')
def transaction_status():
    """Get transaction status distribution"""
    if transactions_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        # Count transactions by status - since there's no status column, 
        # we'll create a success/total metric
        success_rate = {
            'successful': len(transactions_df),
            'total': len(transactions_df)
        }
        return jsonify(success_rate)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/transaction-volume-by-date')
def transaction_volume_by_date():
    """Get transaction volume by date"""
    if transactions_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        if 'date' in transactions_df.columns:
            df_copy = transactions_df.copy()
            df_copy['date'] = pd.to_datetime(df_copy['date'])
            volume = df_copy.groupby(df_copy['date'].dt.date)['amount'].agg(['sum', 'count']).reset_index()
            result = {}
            for idx, row in volume.iterrows():
                result[str(row['date'])] = {'sum': float(row['sum']), 'count': int(row['count'])}
            return jsonify(result)
        else:
            return jsonify({'error': 'No date column found'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/transaction-amount-distribution')
def transaction_amount_distribution():
    """Get transaction amount distribution"""
    if transactions_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        if 'amount' in transactions_df.columns:
            # Create bins for amount distribution
            bins = [0, 1000000, 5000000, 10000000, 50000000, 100000000, float('inf')]
            labels = ['<1M', '1M-5M', '5M-10M', '10M-50M', '50M-100M', '>100M']
            dist = pd.cut(transactions_df['amount'], bins=bins, labels=labels).value_counts().sort_index().to_dict()
            return jsonify(dist)
        else:
            return jsonify({'error': 'No amount column found'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/transaction-metrics')
def transaction_metrics():
    """Get comprehensive transaction metrics"""
    if transactions_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        metrics = {
            'total_transactions': int(len(transactions_df)),
            'total_volume': float(transactions_df['amount'].sum()) if 'amount' in transactions_df.columns else 0,
            'avg_amount': float(transactions_df['amount'].mean()) if 'amount' in transactions_df.columns else 0,
            'median_amount': float(transactions_df['amount'].median()) if 'amount' in transactions_df.columns else 0,
            'std_amount': float(transactions_df['amount'].std()) if 'amount' in transactions_df.columns else 0,
            'max_transaction': float(transactions_df['amount'].max()) if 'amount' in transactions_df.columns else 0,
            'min_transaction': float(transactions_df['amount'].min()) if 'amount' in transactions_df.columns else 0,
        }
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/transaction-by-customer')
def transaction_by_customer():
    """Get transaction count and volume by customer"""
    if transactions_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        by_customer = transactions_df.groupby('customer_id')['amount'].agg(['count', 'sum', 'mean']).reset_index()
        by_customer.columns = ['customer_id', 'transaction_count', 'total_volume', 'avg_amount']
        by_customer = by_customer.sort_values('total_volume', ascending=False).head(20)
        return jsonify(by_customer.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/monthly-transaction-trend')
def monthly_transaction_trend():
    """Get monthly transaction trends"""
    if transactions_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        df_copy = transactions_df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'])
        df_copy['year_month'] = df_copy['date'].dt.to_period('M')
        
        trend = df_copy.groupby('year_month')['amount'].agg(['sum', 'count', 'mean']).reset_index()
        result = []
        for idx, row in trend.iterrows():
            result.append({
                'month': str(row['year_month']),
                'volume': float(row['sum']),
                'count': int(row['count']),
                'avg': float(row['mean'])
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/top-customers-by-transactions')
def top_customers_by_transactions():
    """Get top customers by transaction volume and count"""
    if customer_df is None or transactions_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        # Merge datasets
        customer_txn = transactions_df.groupby('customer_id').agg({
            'amount': ['sum', 'count', 'mean']
        }).reset_index()
        customer_txn.columns = ['customer_id', 'total_volume', 'txn_count', 'avg_amount']
        
        # Join with customer data
        merged = customer_txn.merge(customer_df[['customer_id', 'customer_segment', 'customer_lifetime_value', 'satisfaction_score']], 
                                     on='customer_id', how='left')
        
        # Sort by volume and get top 20
        top = merged.nlargest(20, 'total_volume')[['customer_id', 'customer_segment', 'total_volume', 'txn_count', 'avg_amount', 'customer_lifetime_value', 'satisfaction_score']]
        
        result = []
        for idx, row in top.iterrows():
            result.append({
                'customer_id': int(row['customer_id']),
                'segment': row['customer_segment'],
                'total_volume': float(row['total_volume']),
                'transaction_count': int(row['txn_count']),
                'avg_amount': float(row['avg_amount']),
                'customer_lifetime_value': float(row['customer_lifetime_value']) if pd.notna(row['customer_lifetime_value']) else 0,
                'satisfaction_score': float(row['satisfaction_score']) if pd.notna(row['satisfaction_score']) else 0
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/customer-segment-transaction-analysis')
def customer_segment_transaction_analysis():
    """Analyze transaction patterns by customer segment"""
    if customer_df is None or transactions_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        # Merge datasets
        customer_txn = transactions_df.groupby('customer_id').agg({
            'amount': ['sum', 'count', 'mean']
        }).reset_index()
        customer_txn.columns = ['customer_id', 'total_volume', 'txn_count', 'avg_amount']
        
        merged = customer_txn.merge(customer_df[['customer_id', 'customer_segment']], on='customer_id', how='left')
        
        # Group by segment
        result = {}
        for segment in merged['customer_segment'].unique():
            segment_data = merged[merged['customer_segment'] == segment]
            result[segment] = {
                'avg_volume': float(segment_data['total_volume'].mean()),
                'avg_transaction_count': float(segment_data['txn_count'].mean()),
                'avg_amount_per_transaction': float(segment_data['avg_amount'].mean()),
                'customer_count': int(len(segment_data)),
                'total_segment_volume': float(segment_data['total_volume'].sum())
            }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/customer-satisfaction-vs-transactions')
def customer_satisfaction_vs_transactions():
    """Relate customer satisfaction scores to transaction patterns"""
    if customer_df is None or transactions_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        # Merge datasets
        customer_txn = transactions_df.groupby('customer_id').agg({
            'amount': ['sum', 'count', 'mean']
        }).reset_index()
        customer_txn.columns = ['customer_id', 'total_volume', 'txn_count', 'avg_amount']
        
        merged = customer_txn.merge(customer_df[['customer_id', 'satisfaction_score', 'nps_score', 'churn_probability']], 
                                     on='customer_id', how='left')
        
        # Remove NaN values
        merged = merged.dropna()
        
        # Create satisfaction brackets (scores range from 2-6 in data)
        result = {
            'high_satisfaction': {
                'min_score': 5,
                'avg_volume': float(merged[merged['satisfaction_score'] >= 5]['total_volume'].mean()),
                'avg_txn_count': float(merged[merged['satisfaction_score'] >= 5]['txn_count'].mean()),
                'avg_churn': float(merged[merged['satisfaction_score'] >= 5]['churn_probability'].mean()),
                'count': int(len(merged[merged['satisfaction_score'] >= 5]))
            },
            'medium_satisfaction': {
                'min_score': 4,
                'avg_volume': float(merged[merged['satisfaction_score'] == 4]['total_volume'].mean()),
                'avg_txn_count': float(merged[merged['satisfaction_score'] == 4]['txn_count'].mean()),
                'avg_churn': float(merged[merged['satisfaction_score'] == 4]['churn_probability'].mean()),
                'count': int(len(merged[merged['satisfaction_score'] == 4]))
            },
            'low_satisfaction': {
                'min_score': 2,
                'avg_volume': float(merged[merged['satisfaction_score'] < 4]['total_volume'].mean()),
                'avg_txn_count': float(merged[merged['satisfaction_score'] < 4]['txn_count'].mean()),
                'avg_churn': float(merged[merged['satisfaction_score'] < 4]['churn_probability'].mean()),
                'count': int(len(merged[merged['satisfaction_score'] < 4]))
            }
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/transaction-type-by-segment')
def transaction_type_by_segment():
    """Get transaction type distribution by customer segment"""
    if customer_df is None or transactions_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        # Merge datasets
        merged = transactions_df.merge(customer_df[['customer_id', 'customer_segment']], on='customer_id', how='left')
        
        # Get transaction type counts by segment
        result = {}
        for segment in merged['customer_segment'].unique():
            segment_data = merged[merged['customer_segment'] == segment]
            result[segment] = segment_data['type'].value_counts().to_dict()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/clv-vs-transaction-volume')
def clv_vs_transaction_volume():
    """Correlate customer lifetime value with transaction volume"""
    if customer_df is None or transactions_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        # Get transaction volume per customer
        customer_txn = transactions_df.groupby('customer_id').agg({
            'amount': ['sum', 'count', 'mean']
        }).reset_index()
        customer_txn.columns = ['customer_id', 'total_volume', 'txn_count', 'avg_amount']
        
        # Join with CLV data
        merged = customer_txn.merge(customer_df[['customer_id', 'customer_lifetime_value']], on='customer_id', how='left')
        merged = merged.dropna()
        
        # Create CLV brackets
        result = {
            'platinum': {
                'label': 'Platinum (High CLV)',
                'avg_volume': float(merged[merged['customer_lifetime_value'] > merged['customer_lifetime_value'].quantile(0.75)]['total_volume'].mean()),
                'avg_txn_count': float(merged[merged['customer_lifetime_value'] > merged['customer_lifetime_value'].quantile(0.75)]['txn_count'].mean()),
                'count': int(len(merged[merged['customer_lifetime_value'] > merged['customer_lifetime_value'].quantile(0.75)]))
            },
            'gold': {
                'label': 'Gold (Medium-High CLV)',
                'avg_volume': float(merged[(merged['customer_lifetime_value'] > merged['customer_lifetime_value'].quantile(0.5)) & (merged['customer_lifetime_value'] <= merged['customer_lifetime_value'].quantile(0.75))]['total_volume'].mean()),
                'avg_txn_count': float(merged[(merged['customer_lifetime_value'] > merged['customer_lifetime_value'].quantile(0.5)) & (merged['customer_lifetime_value'] <= merged['customer_lifetime_value'].quantile(0.75))]['txn_count'].mean()),
                'count': int(len(merged[(merged['customer_lifetime_value'] > merged['customer_lifetime_value'].quantile(0.5)) & (merged['customer_lifetime_value'] <= merged['customer_lifetime_value'].quantile(0.75))]))
            },
            'bronze': {
                'label': 'Bronze (Low CLV)',
                'avg_volume': float(merged[merged['customer_lifetime_value'] <= merged['customer_lifetime_value'].quantile(0.5)]['total_volume'].mean()),
                'avg_txn_count': float(merged[merged['customer_lifetime_value'] <= merged['customer_lifetime_value'].quantile(0.5)]['txn_count'].mean()),
                'count': int(len(merged[merged['customer_lifetime_value'] <= merged['customer_lifetime_value'].quantile(0.5)]))
            }
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, port=port, host='0.0.0.0', use_reloader=False)
