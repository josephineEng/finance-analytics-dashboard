# Precision Analytics - Finance Dashboard

A Python-based data analytics dashboard built with Flask that visualizes customer and transaction data using your custom HTML design.

## Features

- **Executive Summary**: Overview of key metrics including total customers, satisfaction scores, NPS, and churn risk
- **Customer Analysis**: Demographics breakdown, gender distribution, education levels, and marital status
- **Churn Risk Analysis**: Identify high-risk customers and analyze churn patterns by segment
- **Interactive Visualizations**: Real-time charts powered by Chart.js
- **RESTful API**: Backend API endpoints for data access and analytics
- **Responsive Design**: Mobile-friendly Material Design UI

## Project Structure

```
try2/
├── app/
│   └── app.py              # Flask application and API endpoints
├── templates/
│   └── dashboard.html      # Interactive dashboard UI
├── data/
│   ├── customer_data.csv   # Customer dataset
│   └── transactions_data.csv # Transaction dataset
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation & Setup

### 1. Install Dependencies

```bash
# Navigate to the project directory
cd c:\Users\user\Desktop\try2

# Install Python packages
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# From the project root directory
python app/app.py
```

The dashboard will be available at: **http://localhost:5000**

## Available API Endpoints

### Dashboard Data

- `GET /api/dashboard-summary` - Get summary metrics
- `GET /api/customers` - Get customers with pagination
- `GET /api/customers?page=1&per_page=10&segment=Gold` - Filter by segment

### Analytics

- `GET /api/analytics/segments` - Customer segmentation analysis
- `GET /api/analytics/income` - Income bracket analytics
- `GET /api/analytics/locations` - Top location analysis
- `GET /api/analytics/nps` - NPS distribution
- `GET /api/analytics/churn` - Churn risk analytics
- `GET /api/analytics/demographics` - Demographic breakdown

## Data Sources

- **customer_data.csv**: Contains ~10,000 customer records with demographics, financial metrics, satisfaction scores, NPS, and churn probability
- **transactions_data.csv**: Contains transaction details and patterns

## Dashboard Sections

### Executive Summary

- Key performance indicators (KPIs)
- Customer segmentation overview
- Churn risk distribution
- Top locations and income brackets

### Customer Analysis

- Age statistics and distribution
- Gender and education breakdown
- Marital status analysis
- Interactive demographic charts

### Churn Risk

- High/Medium/Low risk segments
- Risk distribution by customer segment
- Actionable churn insights

### Demographics

- Comprehensive demographic breakdown
- Education and gender distribution patterns
- Visualizations for all demographic categories

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, Tailwind CSS, Chart.js
- **Data Processing**: Pandas
- **Design System**: Material Design 3

## Customization

### Add New Analytics

Edit `app/app.py` and create new API endpoints:

```python
@app.route('/api/analytics/custom')
def custom_analytics():
    # Your analytics logic
    return jsonify(result)
```

### Modify Dashboard Layout

Edit `templates/dashboard.html` to customize charts, colors, and layout.

### Update Colors

Colors are defined in the Tailwind configuration in the HTML header - modify the color palette as needed.

## Troubleshooting

### Port 5000 in use

Change the port in `app.py`:

```python
app.run(debug=True, port=5001)  # Use a different port
```

### Data loading errors

Ensure CSV files are in the `data/` folder and properly formatted.

### Missing dependencies

Reinstall requirements:

```bash
pip install -r requirements.txt --force-reinstall
```

## Future Enhancements

- Add predictive modeling for churn
- Implement time-series analysis
- Add export functionality (PDF, Excel)
- Create custom report builder
- Add real-time data streaming
- Implement data caching for performance
- Add user authentication

## Support

For issues or questions, refer to:

- Flask documentation: https://flask.palletsprojects.com/
- Pandas documentation: https://pandas.pydata.org/
- Chart.js documentation: https://www.chartjs.org/

## License

This project is provided as-is for data analytics purposes.
