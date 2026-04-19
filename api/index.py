import sys
import os
import json
from flask import Flask, jsonify, request

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the data loader
from app.data_loader import get_data

# Create a minimal Flask app for Vercel
app = Flask(__name__)

# Load data once
customer_df, transactions_df = get_data()

@app.route('/')
def index():
    """Serve main dashboard"""
    # For Vercel, return a simple HTML page
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Finance Analytics Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto p-8">
            <h1 class="text-3xl font-bold mb-8">Finance Analytics Dashboard</h1>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bg-white p-6 rounded-lg shadow">
                    <h2 class="text-xl font-semibold mb-4">Total Customers</h2>
                    <p class="text-3xl font-bold text-blue-600">''' + str(len(customer_df)) + '''</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow">
                    <h2 class="text-xl font-semibold mb-4">Avg Satisfaction</h2>
                    <p class="text-3xl font-bold text-green-600">''' + str(round(customer_df['satisfaction_score'].mean(), 2)) + '''</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow">
                    <h2 class="text-xl font-semibold mb-4">Total Transactions</h2>
                    <p class="text-3xl font-bold text-purple-600">''' + str(len(transactions_df)) + '''</p>
                </div>
            </div>
            <div class="mt-8 bg-white p-6 rounded-lg shadow">
                <h2 class="text-xl font-semibold mb-4">Customer Segments</h2>
                <canvas id="segmentChart"></canvas>
            </div>
        </div>
        <script>
            // Simple chart
            const ctx = document.getElementById('segmentChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ''' + json.dumps(list(customer_df['customer_segment'].value_counts().index)) + ''',
                    datasets: [{
                        label: 'Customers by Segment',
                        data: ''' + json.dumps(list(customer_df['customer_segment'].value_counts().values)) + ''',
                        backgroundColor: ['#3B82F6', '#10B981', '#F59E0B']
                    }]
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/api/dashboard-summary')
def dashboard_summary():
    """Get dashboard summary metrics"""
    summary = {
        'total_customers': len(customer_df),
        'avg_satisfaction': round(customer_df['satisfaction_score'].mean(), 2),
        'avg_nps': round(customer_df['nps_score'].mean(), 2),
        'avg_clv': round(customer_df['customer_lifetime_value'].mean(), 2),
        'churn_risk_customers': len(customer_df[customer_df['churn_probability'] > 0.5]),
        'avg_income': customer_df['income_bracket'].value_counts().to_dict()
    }
    return jsonify(summary)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'customer_count': len(customer_df),
        'transaction_count': len(transactions_df)
    })

# Vercel serverless function handler
def handler(event):
    # Handle Vercel's event format
    try:
        # Extract method, path, and headers from Vercel event
        method = event.get('method', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Create a WSGI environ dict
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'SERVER_NAME': 'vercel.app',
            'SERVER_PORT': '443',
            'wsgi.url_scheme': 'https',
            'wsgi.input': type('MockInput', (), {'read': lambda self, n: body.encode()})(),
            'wsgi.errors': None,
            'wsgi.version': (1, 0),
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }
        
        # Add headers to environ
        for key, value in headers.items():
            environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
        
        # Call the Flask app
        response = {}
        
        def start_response(status, response_headers):
            response['status'] = status
            response['headers'] = response_headers
        
        # Get the response from Flask
        app_iter = app(environ, start_response)
        response_body = b''.join(app_iter) if app_iter else b''
        
        return {
            'statusCode': int(response['status'].split()[0]),
            'headers': dict(response['headers']),
            'body': response_body.decode('utf-8')
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
