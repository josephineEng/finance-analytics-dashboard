import pandas as pd
import os
from functools import lru_cache

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

def load_sample_data():
    """Load a smaller sample of data for faster deployment"""
    # For Render deployment, use fallback data directly to avoid file loading issues
    print("Using fallback demo data for Render deployment")
    return create_fallback_data()

def create_fallback_data():
    """Create minimal fallback data for demo purposes"""
    import numpy as np
    
    # Create sample customer data
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
    
    # Create sample transaction data
    transaction_data = {
        'customer_id': np.random.choice(range(1, 101), 500),
        'amount': np.random.uniform(100, 10000, 500),
        'type': np.random.choice(['Purchase', 'Transfer', 'Payment'], 500),
        'date': pd.date_range('2023-01-01', periods=500, freq='D')
    }
    
    customer_df = pd.DataFrame(customer_data)
    transactions_df = pd.DataFrame(transaction_data)
    
    print("Created fallback demo data")
    return customer_df, transactions_df

@lru_cache(maxsize=1)
def get_data():
    """Lazy loading function with caching"""
    return load_sample_data()
