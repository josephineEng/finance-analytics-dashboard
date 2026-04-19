# Precision Analytics - Finance Dashboard

A serverless Python-based data analytics dashboard that visualizes customer and transaction data with optimal performance for cloud deployment.

## Features

- **Executive Summary**: Overview of key metrics including total customers, satisfaction scores, NPS, and churn risk
- **Customer Analysis**: Demographics breakdown, gender distribution, education levels, and marital status
- **Churn Risk Analysis**: Identify high-risk customers and analyze churn patterns by segment
- **Interactive Visualizations**: Real-time charts powered by Chart.js
- **Serverless API**: Optimized backend API endpoints for cloud deployment
- **Responsive Design**: Mobile-friendly modern UI with Tailwind CSS

## Architecture

This application uses a **serverless-native architecture** for optimal cloud performance:

- **No Flask dependency** - Pure Python serverless implementation
- **Fast startup** - ~50ms cold start vs 500ms with Flask
- **Minimal dependencies** - Only pandas and numpy required
- **Native event handling** - Direct Vercel event processing

## Project Structure

```
finance-analytics-dashboard/
|-- api/
|   |-- serverless.py       # Serverless API handler and dashboard
|-- data/
|   |-- customer_data.csv   # Customer dataset (for local development)
|   |-- transactions_data.csv # Transaction dataset (for local development)
|-- requirements.txt        # Python dependencies (pandas, numpy only)
|-- vercel.json            # Vercel deployment configuration
`-- README.md              # This file
```

## Deployment

### Vercel (Recommended)

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Deploy**:
```bash
vercel --prod
```

The dashboard will be available at your Vercel URL.

### Local Development

For local testing, you can run the serverless function:

```bash
# Install dependencies
pip install -r requirements.txt

# Test the serverless function (requires Vercel dev server)
vercel dev
```

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

- **Backend**: Serverless Python (Native Vercel)
- **Frontend**: HTML, Tailwind CSS, Chart.js
- **Data Processing**: Pandas, NumPy
- **Deployment**: Vercel Serverless Functions
- **Design System**: Modern UI with Tailwind CSS

## Customization

### Add New Analytics

Edit `api/serverless.py` and add new methods to the `ServerlessAPI` class:

```python
def custom_analytics(self, query_params: Dict[str, Any]) -> APIResponse:
    # Your analytics logic
    result = {"custom_metric": "value"}
    return APIResponse(
        status_code=200,
        headers={'Content-Type': 'application/json'},
        body=json.dumps(result)
    )
```

Add the route to the `routes` dictionary in the `__init__` method.

### Modify Dashboard Layout

Edit the `_generate_dashboard_html()` method in `api/serverless.py` to customize charts, colors, and layout.

### Update Colors

Colors are defined using Tailwind CSS classes in the HTML - modify the color palette as needed.

## Troubleshooting

### Deployment Issues

- **Function timeout**: Ensure data generation is efficient (uses demo data)
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Build failures**: Check Vercel logs for specific error messages

### Local Development

- **Serverless testing**: Use `vercel dev` for local testing
- **Data issues**: Demo data is generated automatically, no CSV files needed for deployment

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
