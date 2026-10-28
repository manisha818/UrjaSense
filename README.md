# UrjaSense - AI-Based Energy Consumption Analytics Platform

UrjaSense is a Python-based electricity consumption analytics platform that records electricity readings, analyzes energy usage, estimates electricity charges, detects unusual readings, identifies consumption patterns, and forecasts next-day energy consumption.

The platform provides a FastAPI backend, a SQLite database, and an interactive Streamlit dashboard for energy analytics and visualization.

## Features

- **Electricity Readings:** Store and manage electricity readings for individual devices.
- **Consumption Analytics:** Calculate total energy consumption and analyze device-wise usage.
- **Daily Consumption:** View daily electricity consumption and reading counts.
- **Consumption Trends:** Identify increasing, decreasing, or stable consumption patterns.
- **Anomaly Detection:** Identify unusual electricity readings using anomaly detection techniques.
- **Energy-Saving Recommendations:** Generate recommendations based on available consumption data.
- **Bill Estimation:** Estimate energy charges using consumption in kWh and a user-provided rate per kWh.
- **Usage Pattern Clustering:** Apply K-Means clustering to group completed daily consumption into Low, Medium, and High usage patterns.
- **Energy Forecasting:** Estimate next-day electricity consumption using the average of recent completed daily consumption totals.
- **Forecast Persistence:** Save forecasts in the database for subsequent accuracy evaluation.
- **Forecast Accuracy Tracking:** Compare saved forecasts with recorded actual daily consumption and calculate Mean Absolute Error (MAE).
- **Interactive Dashboard:** Visualize consumption, trends, anomalies, recommendations, estimated bills, usage clusters, and forecasts.
- **REST API:** Expose application functionality through FastAPI endpoints and Swagger documentation.
- **Automated Testing:** Validate application functionality using pytest.
- **Database Migrations:** Manage database schema changes using Alembic.

## Technology Stack

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Alembic
- SQLite
- Streamlit
- Pandas
- Plotly
- NumPy
- Scikit-learn
- Pytest
- HTTPX
- Pydantic Settings

## Project Structure

```text
urjasense/
â”œâ”€â”€ backend/
â”‚   â””â”€â”€ app/
â”‚       â”œâ”€â”€ api/
â”‚       â”‚   â””â”€â”€ v1/
â”‚       â”‚       â”œâ”€â”€ analytics.py
â”‚       â”‚       â”œâ”€â”€ bills.py
â”‚       â”‚       â”œâ”€â”€ clustering.py
â”‚       â”‚       â”œâ”€â”€ consumption.py
â”‚       â”‚       â”œâ”€â”€ devices.py
â”‚       â”‚       â”œâ”€â”€ forecast.py
â”‚       â”‚       â”œâ”€â”€ health.py
â”‚       â”‚       â””â”€â”€ readings.py
â”‚       â”œâ”€â”€ db/
â”‚       â”‚   â”œâ”€â”€ models.py
â”‚       â”‚   â””â”€â”€ session.py
â”‚       â”œâ”€â”€ ml/
â”‚       â”‚   â””â”€â”€ anomaly_detector.py
â”‚       â”œâ”€â”€ services/
â”‚       â”‚   â”œâ”€â”€ aggregation.py
â”‚       â”‚   â”œâ”€â”€ anomaly_service.py
â”‚       â”‚   â”œâ”€â”€ billing.py
â”‚       â”‚   â”œâ”€â”€ clustering_service.py
â”‚       â”‚   â”œâ”€â”€ forecast_service.py
â”‚       â”‚   â””â”€â”€ recommendations.py
â”‚       â”œâ”€â”€ simulator/
â”‚       â””â”€â”€ main.py
â”œâ”€â”€ frontend/
â”‚   â””â”€â”€ dashboard.py
â”œâ”€â”€ migrations/
â”‚   â””â”€â”€ versions/
â”œâ”€â”€ tests/
â”œâ”€â”€ alembic.ini
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ urjasense.db
â””â”€â”€ README.md
```

## Installation and Setup

### 1. Open the project directory

Open PowerShell in the project root directory.

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 5. Apply database migrations

```powershell
python -m alembic upgrade head
```

### 6. Start the backend

```powershell
uvicorn backend.app.main:app --reload
```

The API will be available at:

http://127.0.0.1:8000

### 7. Open API documentation

Visit:

http://127.0.0.1:8000/docs

FastAPI Swagger UI allows you to explore and test the available API endpoints.

### 8. Start the dashboard

Open a second terminal, activate the virtual environment, and run:

```powershell
python -m streamlit run frontend\dashboard.py
```

Open the local URL displayed by Streamlit.

## Forecasting and Accuracy Tracking

### Next-Day Forecast

The forecasting service estimates next-day energy consumption using the average of recent completed daily consumption totals.

A forecast response includes:

- Device ID
- Forecast date
- Predicted consumption in kWh
- Number of historical days used
- Forecasting method
- Status and explanatory message

Forecasts are saved in the `energy_forecasts` database table.

### Forecast Accuracy

The accuracy service compares saved forecasts with actual recorded consumption for matching completed dates.

It reports:

- **Matched Forecast Days:** Number of forecast dates with available actual consumption.
- **Mean Absolute Error (MAE):** Average absolute difference between predicted and actual consumption.
- **Predicted vs Actual Comparison:** Daily predicted consumption, actual consumption, and absolute error.

The MAE formula is:

**MAE = Sum of Absolute Prediction Errors / Number of Matched Days**

Lower MAE indicates smaller average prediction errors.

Accuracy is reported as unavailable when no completed forecast dates have matching actual consumption data. This is expected when a forecast date is still in the future or the corresponding actual readings have not been recorded.

### Forecast API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/forecast/{device_id}` | Generate or retrieve the next-day forecast |
| GET | `/api/v1/forecast/{device_id}/accuracy` | Evaluate accuracy using matching completed forecast dates |

These endpoints can be explored through the Swagger documentation.

## Testing

Run the automated test suite from the project root:

```powershell
python -m pytest -v --ignore=backup_task1_20261014_202012
```

The backup directory is excluded because it may contain older tests or files.

The current verified test result is **49 passed**. Run the command again after making code changes to verify the latest state.

## Bill Estimation

Energy charges are estimated using:

**Energy Charges = Consumption (kWh) Ã— Rate per kWh**

For example, if consumption is 69.080 kWh and the entered rate is â‚¹9.50 per kWh:

**Estimated Energy Charges = â‚¹656.26**

This is an energy-charge estimate, not necessarily the final electricity bill. Actual bills may include fixed charges, taxes, subsidies, and other tariff rules.

## Important Notes

- The application uses simulated electricity readings for development and testing.
- Forecasts are estimates based on historical consumption, not guaranteed predictions.
- Forecast accuracy requires matching forecasts and actual consumption for completed dates.
- Anomaly detection and clustering results depend on the amount and quality of available data.
- Bill estimates depend on the user-provided rate and may not reflect the complete applicable electricity tariff.
- The project is intended for learning, demonstration, and further development.

## Future Improvements

- Integration with real smart meters and IoT devices.
- More advanced forecasting models and evaluation metrics.
- More detailed tariff-based bill calculations.
- Improved anomaly detection using larger datasets.
- Additional historical comparisons and visualizations.
- Deployment for remote access.

## License

No license has been specified yet.

