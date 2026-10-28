# UrjaSense - AI-Based Energy Consumption Analytics Platform

UrjaSense is a Python-based electricity consumption analytics platform developed as a college project by three students. It records electricity readings, analyzes energy usage, estimates electricity bills, detects unusual readings, identifies consumption patterns, and forecasts next-day energy consumption.

The project uses simulated electricity data to demonstrate how software and machine learning techniques can help users understand and monitor energy consumption.

## Features

- **Device and Reading Management:** Store device details and electricity readings.
- **Energy Analytics:** Analyze electricity consumption using recorded readings.
- **Daily Consumption:** View daily electricity usage.
- **Consumption Trends:** Analyze changes in energy consumption over time.
- **Anomaly Detection:** Identify unusual readings using the Isolation Forest algorithm.
- **Energy-Saving Recommendations:** Generate suggestions based on detected usage patterns and readings.
- **Electricity Bill Estimation:** Estimate electricity charges using consumption and a configurable rate.
- **Usage Pattern Clustering:** Group consumption patterns into Low, Medium, and High categories using K-Means clustering.
- **Next-Day Forecasting:** Predict next-day electricity consumption using recent daily consumption averages.
- **Forecast Storage:** Save generated forecasts in the database.
- **Forecast Accuracy Tracking:** Compare saved forecasts with actual consumption and calculate Mean Absolute Error (MAE) when matching data is available.
- **Interactive Dashboard:** Explore consumption analytics, trends, forecasts, and other results through Streamlit.
- **REST API:** Access backend functionality through FastAPI endpoints.
- **Database Migrations:** Manage database schema changes using Alembic.
- **Automated Testing:** Test application functionality using Pytest and HTTPX.

## Technology Stack

| Technology | Purpose |
| --- | --- |
| Python | Core programming language |
| FastAPI | Backend REST API |
| Uvicorn | Backend development server |
| SQLAlchemy | Database operations and ORM |
| SQLite | Data storage |
| Alembic | Database migrations |
| Streamlit | Interactive dashboard |
| Pandas | Data processing and analysis |
| NumPy | Numerical operations |
| Plotly | Data visualization |
| Scikit-learn | Machine learning algorithms |
| Pydantic Settings | Application configuration |
| Pytest | Automated testing |
| HTTPX | API testing |

## Project Structure

```text
UrjaSense/
|
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |   |-- v1/
|   |   |-- core/
|   |   |-- db/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- services/
|   |   |-- simulator/
|   |   |-- main.py
|   |
|   |-- db/
|
|-- frontend/
|   |-- dashboard.py
|
|-- migrations/
|   |-- versions/
|
|-- tests/
|
|-- alembic.ini
|-- requirements.txt
|-- README.md
|-- .gitignore
```

The structure above shows the main project directories. Some directories may contain additional files and modules.

## Requirements

Before running the project, make sure you have:

- Python installed
- Git installed (if cloning the repository)
- Visual Studio Code or another code editor

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/manisha818/UrjaSense.git
cd UrjaSense
```

If the project is already present on your computer, open the existing UrjaSense folder in VS Code instead.

### 2. Create a Virtual Environment

On Windows, run:

```powershell
python -m venv .venv
```

### 3. Activate the Virtual Environment

For PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If activation is blocked by the PowerShell execution policy, use the VS Code Command Prompt terminal and run:

```cmd
.venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Apply Database Migrations

```bash
python -m alembic upgrade head
```

This applies the database schema migrations configured in the project.

### 6. Start the Backend

```bash
python -m uvicorn backend.app.main:app --reload
```

The backend development server should be available at:

- API base URL: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs

Keep the backend terminal running while using the dashboard.

### 7. Start the Dashboard

Open a second terminal in VS Code, activate the same virtual environment, and run:

```bash
python -m streamlit run frontend/dashboard.py
```

Streamlit will display the local dashboard URL in the terminal. Open that URL in your browser.

## API Endpoints

The backend provides versioned REST API endpoints for health checks, device and reading management, analytics, bill estimation, anomaly detection, recommendations, usage-pattern clustering, and forecasting.

Two forecasting endpoints are:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v1/forecast/{device_id}` | Generate and store a next-day consumption forecast |
| GET | `/api/v1/forecast/{device_id}/accuracy` | Evaluate saved forecasts against actual consumption |

Replace `{device_id}` with a valid device ID.

For the available endpoints, request parameters, and response schemas, start the backend and open:

http://127.0.0.1:8000/docs

## Forecasting and Accuracy Tracking

UrjaSense estimates next-day electricity consumption using recent completed daily consumption totals.

The forecasting workflow:

1. Reads available consumption data for a device.
2. Calculates a prediction using the recent daily average.
3. Saves the forecast in the `energy_forecasts` database table.
4. Compares saved forecasts with actual consumption when matching completed daily data becomes available.
5. Calculates Mean Absolute Error (MAE) to measure prediction error.

MAE represents the average absolute difference between predicted and actual consumption. A lower MAE indicates smaller prediction errors for the evaluated records.

Forecast accuracy cannot be calculated when suitable matching actual consumption data is unavailable.

## Electricity Bill Estimation

The application estimates electricity charges using the recorded or calculated consumption and the configured per-unit rate.

**Formula:**

```text
Estimated Bill = Energy Consumption (kWh) x Rate per kWh
```

For example, if consumption is 69.080 kWh and the configured rate is Rs. 9.50 per kWh:

```text
69.080 x 9.50 = Rs. 656.26
```

This is an illustrative estimate. Actual electricity bills may differ because of fixed charges, taxes, slab rates, subsidies, and other applicable fees.

## Machine Learning Components

### 1. Anomaly Detection

Isolation Forest is used to identify readings that differ significantly from the observed data. These readings can be investigated for unusual consumption behavior.

### 2. Consumption Pattern Clustering

K-Means groups consumption data into Low, Medium, and High usage patterns based on the features used by the application.

### 3. Consumption Forecasting

The current forecasting method uses recent completed daily consumption averages. It provides a baseline prediction and is not a guarantee of future usage.

## Running Tests

From the project root, activate the virtual environment and run:

```bash
python -m pytest -v --ignore=backup_task1_20261014_202012
```

This command excludes the specified backup directory from test discovery.

The test results displayed in the terminal show how many tests passed or failed in the current run. Run the tests again after making code changes to verify the current project state.

## Limitations

- The current project uses simulated electricity data rather than live hardware readings.
- Predictions depend on the available historical consumption data.
- Forecast accuracy requires matching actual consumption records.
- Bill calculations are estimates and may not represent the final utility bill.
- Anomaly detection identifies unusual data points; it does not independently confirm the cause of an unusual reading.

## Future Improvements

Possible future enhancements include:

- Integration with real electricity-monitoring hardware.
- Live energy readings through an IoT device.
- Improved forecasting using additional historical features.
- More detailed energy-saving recommendations.
- User authentication and role-based access.
- Additional dashboard filters and reporting options.

## Project Purpose

UrjaSense was developed as a third-year Computer Science and Information Technology college project to apply Python programming, backend development, database management, data analytics, visualization, and introductory machine learning to an electricity consumption use case.

## License

No open-source license has been specified for this repository.
