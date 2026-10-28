# UrjaSense — AI-Based Energy Consumption Analytics Platform

## About the Project

UrjaSense is a college project developed by a team of three students. It is a Python-based platform that analyzes electricity consumption data and presents useful information through a dashboard.

The project uses simulated electricity readings to demonstrate energy analytics, unusual consumption detection, usage patterns, bill estimation, and next-day consumption forecasting. It currently works with simulated data and does not require live IoT hardware.

## Features

- **Energy Consumption Analytics:** View electricity consumption data and daily usage trends.
- **Interactive Dashboard:** Explore readings, consumption summaries, charts, and analytics.
- **Electricity Bill Estimation:** Estimate the electricity bill using energy consumption and a per-unit rate.
- **Anomaly Detection:** Use Isolation Forest to identify potentially unusual readings.
- **Usage Pattern Clustering:** Use K-Means to group consumption patterns into Low, Medium, and High categories.
- **Energy-Saving Recommendations:** Generate suggestions based on consumption readings and historical usage.
- **Next-Day Forecasting:** Estimate upcoming daily consumption using recent historical averages.
- **Forecast Accuracy Tracking:** Compare saved forecasts with actual consumption and calculate Mean Absolute Error (MAE).
- **REST API:** Access supported project features through FastAPI endpoints.
- **Automated Testing:** Use pytest to test application functionality.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | Backend and REST API |
| SQLite | Database |
| SQLAlchemy | Database operations and ORM |
| Alembic | Database migrations |
| Streamlit | Interactive dashboard |
| Pandas and NumPy | Data processing |
| Plotly | Data visualization |
| Scikit-learn | Anomaly detection and clustering |
| Pytest and HTTPX | Testing |

## Project Structure

```text
UrjaSense/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── simulator/
│   │   └── main.py
│   └── db/
├── frontend/
│   └── dashboard.py
├── migrations/
│   └── versions/
├── tests/
├── alembic.ini
├── requirements.txt
├── README.md
└── .gitignore
```

This is a simplified view of the project structure.

## Requirements

- Python installed on your system
- Git
- The packages listed in `requirements.txt`

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/manisha818/UrjaSense.git
cd UrjaSense
```

### 2. Create and Activate a Virtual Environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the following command in the current terminal session and try activation again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python -m alembic upgrade head
```

### 5. Start the Backend

Open a terminal in the project root and run:

```bash
python -m uvicorn backend.app.main:app --reload
```

The backend normally runs at `http://127.0.0.1:8000`.

You can check the available API documentation at:

`http://127.0.0.1:8000/docs`

### 6. Start the Dashboard

Keep the backend running. Open a second terminal in the project root, activate the same virtual environment if needed, and run:

```bash
python -m streamlit run frontend/dashboard.py
```

Streamlit will display the local dashboard URL in the terminal. Open that URL in your browser.

## API Overview

The application provides API endpoints for supported features such as health checks, devices, readings, analytics, bill estimation, anomaly detection, recommendations, and forecasting.

The following forecast endpoints are included:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Check backend health |
| GET | `/api/v1/forecast/{device_id}` | Generate a next-day consumption forecast |
| GET | `/api/v1/forecast/{device_id}/accuracy` | Evaluate saved forecasts against actual consumption |

Other endpoint paths and parameters can be checked in the FastAPI documentation at `/docs` while the backend is running.

## Consumption Forecasting

UrjaSense estimates next-day electricity consumption using recent historical daily consumption data. The forecast is saved so that it can later be compared with actual consumption.

This is a baseline forecasting approach intended for the college project. Its predictions depend on the available historical data and may not capture seasonal changes or complex consumption patterns.

## Forecast Accuracy

The project evaluates saved forecasts against actual daily consumption using Mean Absolute Error (MAE).

```text
MAE = Sum of absolute prediction errors / Number of evaluated predictions
```

A lower MAE indicates that the evaluated forecasts are closer to actual consumption. Accuracy results depend on the amount and quality of available data.

## Electricity Bill Estimation

The dashboard estimates the bill using the recorded energy consumption and the configured rate per unit.

```text
Estimated Bill = Energy Consumption (kWh) × Rate per kWh
```

For example, if consumption is 69.080 kWh and the configured rate is ₹9.50 per kWh:

```text
69.080 × 9.50 = ₹656.26
```

This is an illustrative project calculation, not an official electricity bill. Actual bills may include additional charges, taxes, slabs, or adjustments.

## Running Tests

From the project root, run:

```bash
python -m pytest -v --ignore=backup_task1_20261014_202012
```

The command excludes the specified backup directory from test discovery. Test results may vary if the code or environment has changed.

## Current Limitations

- The current project uses simulated electricity readings rather than live hardware data.
- Forecasting uses a simple historical-average approach.
- Bill estimates depend on the configured rate and do not represent every component of an actual electricity bill.
- Detection and clustering results depend on the data available to the application.

## Future Improvements

- Integrate real electricity sensors and IoT devices.
- Explore more advanced forecasting methods.
- Improve recommendations using additional consumption patterns.
- Add user authentication and more detailed reporting.
- Evaluate the models with larger and more varied datasets.

## Project Purpose

UrjaSense demonstrates how Python, data analytics, machine learning, a REST API, and an interactive dashboard can be combined to analyze electricity consumption.

The project was developed for academic learning and can be extended with real-world data and additional features.
