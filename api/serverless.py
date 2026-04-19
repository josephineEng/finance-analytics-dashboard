import json
import sys
import os
from dataclasses import dataclass
from typing import Dict, Any, List
import pandas as pd
import numpy as np

# Generate demo data directly (no external dependencies)
def generate_demo_data():
    """Generate demo data for serverless deployment"""
    np.random.seed(42)  # For consistent data
    
    # Customer data
    customer_data = {
        'customer_id': range(1, 101),
        'customer_segment': np.random.choice(['Gold', 'Silver', 'Bronze'], 100),
        'satisfaction_score': np.random.uniform(2, 6, 100),
        'nps_score': np.random.uniform(-10, 10, 100),
        'customer_lifetime_value': np.random.uniform(1000, 10000, 100),
        'churn_probability': np.random.uniform(0, 1, 100),
        'income_bracket': np.random.choice(['Low', 'Medium', 'High'], 100),
        'location': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston'], 100),
        'gender': np.random.choice(['Male', 'Female'], 100),
        'education_level': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], 100),
        'marital_status': np.random.choice(['Single', 'Married', 'Divorced'], 100),
        'age': np.random.randint(18, 80, 100)
    }
    
    # Transaction data
    transaction_data = {
        'customer_id': np.random.choice(range(1, 101), 500),
        'amount': np.random.uniform(100, 10000, 500),
        'type': np.random.choice(['Purchase', 'Transfer', 'Payment'], 500),
        'date': pd.date_range('2023-01-01', periods=500, freq='D')
    }
    
    customer_df = pd.DataFrame(customer_data)
    transactions_df = pd.DataFrame(transaction_data)
    
    return customer_df, transactions_df

# Load data once at startup
customer_df, transactions_df = generate_demo_data()

@dataclass
class APIResponse:
    """Standard API response for serverless functions"""
    status_code: int
    headers: Dict[str, str]
    body: str

class ServerlessAPI:
    """Serverless-specific API handler without Flask dependency"""
    
    def __init__(self):
        self.routes = {
            '/': self.dashboard,
            '/health': self.health,
            '/api/dashboard-summary': self.dashboard_summary,
            '/api/customers': self.get_customers,
            '/api/analytics/segments': self.segment_analytics,
            '/api/analytics/churn': self.churn_analytics,
            '/api/analytics/demographics': self.demographics_analytics,
            '/api/analytics/nps': self.nps_analytics,
        }
    
    def handle_request(self, event: Dict[str, Any]) -> APIResponse:
        """Main request handler for serverless functions"""
        try:
            method = event.get('method', 'GET')
            path = event.get('path', '/')
            query_params = event.get('queryParameters', {})
            
            # Route handling
            if path in self.routes:
                if method == 'GET':
                    return self.routes[path](query_params)
                else:
                    return self._error_response(405, "Method not allowed")
            else:
                return self._error_response(404, "Not found")
                
        except Exception as e:
            return self._error_response(500, f"Internal server error: {str(e)}")
    
    def dashboard(self, query_params: Dict[str, Any]) -> APIResponse:
        """Serve main dashboard HTML"""
        html_content = self._generate_dashboard_html()
        return APIResponse(
            status_code=200,
            headers={'Content-Type': 'text/html'},
            body=html_content
        )
    
    def health(self, query_params: Dict[str, Any]) -> APIResponse:
        """Health check endpoint"""
        return APIResponse(
            status_code=200,
            headers={'Content-Type': 'application/json'},
            body=json.dumps({
                'status': 'healthy',
                'customer_count': len(customer_df),
                'transaction_count': len(transactions_df)
            })
        )
    
    def dashboard_summary(self, query_params: Dict[str, Any]) -> APIResponse:
        """Get dashboard summary metrics"""
        summary = {
            'total_customers': len(customer_df),
            'avg_satisfaction': round(customer_df['satisfaction_score'].mean(), 2),
            'avg_nps': round(customer_df['nps_score'].mean(), 2),
            'avg_clv': round(customer_df['customer_lifetime_value'].mean(), 2),
            'churn_risk_customers': len(customer_df[customer_df['churn_probability'] > 0.5]),
            'avg_income': customer_df['income_bracket'].value_counts().to_dict()
        }
        return APIResponse(
            status_code=200,
            headers={'Content-Type': 'application/json'},
            body=json.dumps(summary)
        )
    
    def get_customers(self, query_params: Dict[str, Any]) -> APIResponse:
        """Get customers with pagination"""
        page = int(query_params.get('page', 1))
        per_page = int(query_params.get('per_page', 10))
        segment = query_params.get('segment', None)
        
        df = customer_df.copy()
        
        # Filter by segment
        if segment and 'customer_segment' in df.columns:
            df = df[df['customer_segment'] == segment]
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        
        customers = df.iloc[start:end].to_dict('records')
        
        return APIResponse(
            status_code=200,
            headers={'Content-Type': 'application/json'},
            body=json.dumps({
                'customers': customers,
                'total': len(df),
                'page': page,
                'per_page': per_page
            })
        )
    
    def segment_analytics(self, query_params: Dict[str, Any]) -> APIResponse:
        """Get customer segmentation analytics"""
        segments = customer_df['customer_segment'].value_counts().to_dict()
        segment_stats = {}
        
        for segment in customer_df['customer_segment'].unique():
            segment_data = customer_df[customer_df['customer_segment'] == segment]
            segment_stats[segment] = {
                'count': len(segment_data),
                'avg_satisfaction': round(segment_data['satisfaction_score'].mean(), 2),
                'avg_clv': round(segment_data['customer_lifetime_value'].mean(), 2),
                'avg_nps': round(segment_data['nps_score'].mean(), 2),
                'churn_risk': len(segment_data[segment_data['churn_probability'] > 0.5])
            }
        
        return APIResponse(
            status_code=200,
            headers={'Content-Type': 'application/json'},
            body=json.dumps(segment_stats)
        )
    
    def churn_analytics(self, query_params: Dict[str, Any]) -> APIResponse:
        """Get churn risk analytics"""
        high_risk = len(customer_df[customer_df['churn_probability'] > 0.7])
        medium_risk = len(customer_df[(customer_df['churn_probability'] > 0.4) & (customer_df['churn_probability'] <= 0.7)])
        low_risk = len(customer_df[customer_df['churn_probability'] <= 0.4])
        
        return APIResponse(
            status_code=200,
            headers={'Content-Type': 'application/json'},
            body=json.dumps({
                'high_risk': high_risk,
                'medium_risk': medium_risk,
                'low_risk': low_risk,
                'total': len(customer_df)
            })
        )
    
    def demographics_analytics(self, query_params: Dict[str, Any]) -> APIResponse:
        """Get demographic analytics"""
        demographics = {
            'gender': customer_df['gender'].value_counts().to_dict(),
            'education': customer_df['education_level'].value_counts().to_dict(),
            'marital_status': customer_df['marital_status'].value_counts().to_dict(),
            'age_stats': {
                'mean': round(customer_df['age'].mean(), 2),
                'median': float(customer_df['age'].median()),
                'min': int(customer_df['age'].min()),
                'max': int(customer_df['age'].max())
            }
        }
        
        return APIResponse(
            status_code=200,
            headers={'Content-Type': 'application/json'},
            body=json.dumps(demographics)
        )
    
    def nps_analytics(self, query_params: Dict[str, Any]) -> APIResponse:
        """Get NPS distribution"""
        nps_bins = [-100, -1, 0, 6, 8, 10]
        nps_dist = pd.cut(customer_df['nps_score'], bins=nps_bins, labels=['Detractors', 'Passive', 'Promoters']).value_counts().to_dict()
        
        return APIResponse(
            status_code=200,
            headers={'Content-Type': 'application/json'},
            body=json.dumps(nps_dist)
        )
    
    def _generate_dashboard_html(self) -> str:
        """Generate dashboard HTML content"""
        segment_counts = customer_df['customer_segment'].value_counts()
        segment_labels = list(segment_counts.index)
        segment_values = list(segment_counts.values)
        
        return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Finance Analytics Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
    </style>
</head>
<body class="bg-gray-50">
    <div class="min-h-screen">
        <!-- Header -->
        <header class="bg-white shadow-sm border-b">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center py-6">
                    <h1 class="text-3xl font-bold text-gray-900">Finance Analytics Dashboard</h1>
                    <div class="flex items-center space-x-4">
                        <span class="text-sm text-gray-500">Serverless Edition</span>
                        <span class="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">Live</span>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <!-- KPI Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                                <span class="text-white text-sm font-medium">C</span>
                            </div>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Total Customers</p>
                            <p class="text-2xl font-bold text-gray-900">{len(customer_df)}</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                                <span class="text-white text-sm font-medium">S</span>
                            </div>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Avg Satisfaction</p>
                            <p class="text-2xl font-bold text-gray-900">{round(customer_df['satisfaction_score'].mean(), 2)}</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                                <span class="text-white text-sm font-medium">T</span>
                            </div>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Total Transactions</p>
                            <p class="text-2xl font-bold text-gray-900">{len(transactions_df)}</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <div class="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                                <span class="text-white text-sm font-medium">!</span>
                            </div>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Churn Risk</p>
                            <p class="text-2xl font-bold text-gray-900">{len(customer_df[customer_df['churn_probability'] > 0.5])}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts Section -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- Customer Segments Chart -->
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-lg font-semibold text-gray-900 mb-4">Customer Segments</h2>
                    <canvas id="segmentChart" width="400" height="200"></canvas>
                </div>
                
                <!-- Satisfaction Distribution -->
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-lg font-semibold text-gray-900 mb-4">Satisfaction Distribution</h2>
                    <canvas id="satisfactionChart" width="400" height="200"></canvas>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="mt-8 bg-white rounded-lg shadow">
                <div class="px-6 py-4 border-b border-gray-200">
                    <h2 class="text-lg font-semibold text-gray-900">System Status</h2>
                </div>
                <div class="px-6 py-4">
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-600">Serverless Function Status</span>
                        <span class="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">Operational</span>
                    </div>
                    <div class="flex items-center justify-between mt-2">
                        <span class="text-sm text-gray-600">Data Source</span>
                        <span class="text-sm text-gray-900">Demo Data (100 customers)</span>
                    </div>
                    <div class="flex items-center justify-between mt-2">
                        <span class="text-sm text-gray-600">Response Time</span>
                        <span class="text-sm text-gray-900">&lt;100ms</span>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        // Customer Segments Chart
        const segmentCtx = document.getElementById('segmentChart').getContext('2d');
        new Chart(segmentCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(segment_labels)},
                datasets: [{{
                    data: {json.dumps(segment_values)},
                    backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});

        // Satisfaction Distribution Chart
        const satisfactionCtx = document.getElementById('satisfactionChart').getContext('2d');
        const satisfactionData = {json.dumps(list(customer_df['satisfaction_score'].values))};
        new Chart(satisfactionCtx, {{
            type: 'bar',
            data: {{
                labels: satisfactionData.map((_, i) => `Customer ${{i+1}}`),
                datasets: [{{
                    label: 'Satisfaction Score',
                    data: satisfactionData,
                    backgroundColor: satisfactionData.map(score => 
                        score >= 5 ? '#10B981' : score >= 4 ? '#F59E0B' : '#EF4444'
                    ),
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 6
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        '''
    
    def _error_response(self, status_code: int, message: str) -> APIResponse:
        """Create error response"""
        return APIResponse(
            status_code=status_code,
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'error': message})
        )

# Initialize the serverless API
api = ServerlessAPI()

# Main handler function for Vercel
def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """Vercel serverless function handler"""
    response = api.handle_request(event)
    
    return {
        'statusCode': response.status_code,
        'headers': response.headers,
        'body': response.body
    }
