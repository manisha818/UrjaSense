
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# -------------------------------
# Page Configuration
# -------------------------------

st.set_page_config(
    page_title="UrjaSense Dashboard",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ UrjaSense")
st.subheader("Electricity Consumption Analytics")
st.caption(
    "Monitor energy usage, daily consumption, trends, "
    "anomalies, and energy-saving recommendations."
)

# -------------------------------
# Sidebar
# -------------------------------

device_id = st.sidebar.number_input(
    "Device ID",
    min_value=1,
    value=1,
    step=1,
)

if st.sidebar.button("Refresh dashboard"):
    st.cache_data.clear()
    st.rerun()


# -------------------------------
# API Helper
# -------------------------------

@st.cache_data(ttl=10)
def fetch_api(endpoint):
    response = requests.get(
        f"{API_BASE_URL}/{endpoint}",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


# -------------------------------
# Fetch Consumption Data
# -------------------------------

try:
    summary = fetch_api(
        f"consumption/summary?device_id={device_id}"
    )
    daily_data = fetch_api(
        f"consumption/daily/{device_id}"
    )
    trend_data = fetch_api(
        f"consumption/trends/{device_id}"
    )

except requests.RequestException as exc:
    st.error(
        "Could not connect to the UrjaSense API. "
        "Make sure the FastAPI server is running."
    )
    st.caption(f"Details: {exc}")
    st.stop()


# -------------------------------
# Consumption Summary
# -------------------------------

total_energy = summary.get("total_consumption_kwh", 0)
reading_count = summary.get("reading_count", 0)
trend = trend_data.get("trend", "no_data")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Consumption",
    f"{total_energy:.3f} kWh",
)

col2.metric(
    "Total Readings",
    reading_count,
)

col3.metric(
    "Consumption Trend",
    trend.replace("_", " ").title(),
)

st.divider()


# -------------------------------
# Daily Consumption Chart
# -------------------------------

st.subheader("📊 Daily Energy Consumption")

if daily_data:
    df = pd.DataFrame(daily_data)
    df["date"] = pd.to_datetime(df["date"])

    fig = px.bar(
        df,
        x="date",
        y="total_consumption_kwh",
        title="Daily Consumption (kWh)",
        labels={
            "date": "Date",
            "total_consumption_kwh": "Energy (kWh)",
        },
        hover_data=["reading_count"],
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Consumption (kWh)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.subheader("Daily Consumption Records")

    display_df = df.copy()
    display_df["date"] = display_df["date"].dt.strftime(
        "%Y-%m-%d"
    )

    display_df = display_df.rename(
        columns={
            "date": "Date",
            "total_consumption_kwh": "Consumption (kWh)",
            "reading_count": "Reading Count",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info("No consumption data available for this device.")


st.divider()


# -------------------------------
# Trend Analysis
# -------------------------------

st.subheader("📈 Trend Analysis")

if trend == "increasing":
    st.warning("Energy consumption is increasing.")

elif trend == "decreasing":
    st.success("Energy consumption is decreasing.")

elif trend == "stable":
    st.info("Energy consumption is stable.")

elif trend == "insufficient_data":
    st.info(
        "More completed daily data is required "
        "to calculate the trend."
    )

else:
    st.info("No trend is available yet.")

st.caption(
    trend_data.get(
        "message",
        "Trend information unavailable.",
    )
)


st.divider()


# -------------------------------
# Anomaly Detection
# -------------------------------

st.subheader("🚨 Anomaly Detection")

st.write(
    "Enter electricity readings to check for unusual patterns."
)

with st.form("anomaly_detection_form"):
    voltage = st.number_input(
        "Voltage (V)",
        min_value=0.0,
        value=230.0,
        step=1.0,
    )

    current = st.number_input(
        "Current (A)",
        min_value=0.0,
        value=2.0,
        step=0.1,
    )

    power_w = st.number_input(
        "Power (W)",
        min_value=0.0,
        value=460.0,
        step=1.0,
    )

    check_anomaly_button = st.form_submit_button(
        "Check Reading"
    )


if check_anomaly_button:
    payload = {
        "device_id": int(device_id),
        "voltage": voltage,
        "current": current,
        "power_w": power_w,
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/analytics/anomalies/check",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        anomaly_result = response.json()

        if anomaly_result.get("is_anomaly"):
            st.warning(
                "⚠️ Unusual electricity reading detected."
            )
        else:
            st.success(
                "✅ No unusual pattern detected."
            )

        st.write(
            anomaly_result.get(
                "message",
                "Anomaly check completed.",
            )
        )

        with st.expander("View detection details"):
            st.json(anomaly_result)

    except requests.RequestException as exc:
        st.error(f"Anomaly check failed: {exc}")

        if exc.response is not None:
            st.caption(exc.response.text)


st.divider()


# -------------------------------
# Energy-Saving Recommendations
# -------------------------------

st.subheader("💡 Energy-Saving Recommendations")

if st.button("Get Recommendations"):
    try:
        response = requests.get(
            f"{API_BASE_URL}/analytics/recommendations/{device_id}",
            timeout=15,
        )
        response.raise_for_status()

        recommendations = response.json()

        if isinstance(recommendations, dict):
            st.caption(
                f"Device ID: "
                f"{recommendations.get('device_id', device_id)}"
            )

            data_status = recommendations.get(
                "data_status",
                "not_available",
            )

            st.write(
                f"**Data Status:** "
                f"{data_status.replace('_', ' ').title()}"
            )

            col1, col2 = st.columns(2)

            col1.metric(
                "Readings Analyzed",
                recommendations.get("readings_analyzed", 0),
            )

            latest_power = recommendations.get("latest_power_w")

            col2.metric(
                "Latest Power",
                (
                    f"{latest_power:.2f} W"
                    if latest_power is not None
                    else "N/A"
                ),
            )

            recommendation_list = recommendations.get(
                "recommendations",
                [],
            )

            if recommendation_list:
                st.markdown("### Recommendations")

                for index, item in enumerate(
                    recommendation_list,
                    start=1,
                ):
                    if isinstance(item, dict):
                        with st.container(border=True):
                            st.markdown(
                                f"**{index}. {item.get('title', 'Energy Recommendation')}**"
                            )

                            priority = item.get(
                                "priority",
                                "normal",
                            ).title()

                            time_horizon = item.get(
                                "time_horizon",
                                "current",
                            ).title()

                            st.caption(
                                f"Priority: {priority} | "
                                f"Time Horizon: {time_horizon}"
                            )

                            st.write(
                                item.get(
                                    "message",
                                    "No additional details available.",
                                )
                            )

                    else:
                        st.write(f"{index}. {item}")

            else:
                st.info(
                    "No energy-saving recommendations available "
                    "for this device."
                )

        elif isinstance(recommendations, list):
            if recommendations:
                for index, item in enumerate(
                    recommendations,
                    start=1,
                ):
                    if isinstance(item, dict):
                        with st.container(border=True):
                            st.markdown(
                                f"**{index}. "
                                f"{item.get('title', 'Recommendation')}**"
                            )
                            st.write(
                                item.get("message", str(item))
                            )
                    else:
                        st.write(f"{index}. {item}")

            else:
                st.info("No recommendations available.")

        else:
            st.write(recommendations)

    except requests.RequestException as exc:
        st.error(
            f"Could not fetch recommendations: {exc}"
        )

        if exc.response is not None:
            st.caption(exc.response.text)
            
# -------------------------------
# Bill Estimation
# -------------------------------

st.divider()
st.subheader("🧾 Electricity Bill Estimation")

st.write(
    "Estimate your electricity energy charges "
    "using consumption and per-unit rate."
)

st.metric(
    "Consumption Used for Estimate",
    f"{total_energy:.3f} kWh",
)

with st.form("bill_estimation_form"):
    rate_per_kwh = st.number_input(
        "Electricity Rate (₹ per kWh)",
        min_value=0.0,
        value=5.0,
        step=0.5,
    )

    estimate_button = st.form_submit_button(
        "Calculate Estimated Bill"
    )

if estimate_button:
    bill_payload = {
        "consumption_kwh": float(total_energy),
        "rate_per_kwh": float(rate_per_kwh),
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/bills/estimate",
            json=bill_payload,
            timeout=15,
        )
        response.raise_for_status()

        bill_data = response.json()

        st.success("Bill estimate calculated successfully.")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Consumption",
            f"{bill_data['consumption_kwh']:.3f} kWh",
        )

        col2.metric(
            "Energy Charges",
            f"₹{bill_data['energy_charge']:.2f}",
        )

        col3.metric(
            "Estimated Total",
            f"₹{bill_data['estimated_total']:.2f}",
        )

        st.caption(
            "Estimate only. Actual electricity bills may include "
            "fixed charges, taxes, and other applicable charges."
        )

    except requests.RequestException as exc:
        st.error(f"Bill estimation failed: {exc}")

        if exc.response is not None:
            st.caption(exc.response.text)

# -------------------------------
# Usage Pattern Clustering
# -------------------------------

st.divider()
st.subheader("Usage Pattern Clustering")

st.write(
    "Identify low, medium, and high electricity usage "
    "patterns from completed daily readings."
)

if st.button("Analyze Usage Patterns"):
    try:
        response = requests.get(
            f"{API_BASE_URL}/clustering/usage-patterns/{device_id}",
            timeout=30,
        )
        response.raise_for_status()
        clustering_data = response.json()

        status = clustering_data.get("status", "unknown")
        st.info(clustering_data.get("message", "Analysis completed."))

        if status == "success":
            clusters = clustering_data.get("clusters", [])
            daily_patterns = clustering_data.get("daily_patterns", [])

            if clusters:
                st.markdown("### Usage Pattern Summary")

                cols = st.columns(len(clusters))

                for col, cluster in zip(cols, clusters):
                    col.metric(
                        f"{cluster['usage_pattern']} Usage",
                        f"{cluster['average_daily_consumption_kwh']:.3f} kWh",
                        f"{cluster['days_count']} days",
                    )

                st.markdown("### Daily Usage Classification")

                pattern_df = pd.DataFrame(daily_patterns)

                pattern_df = pattern_df.rename(
                    columns={
                        "date": "Date",
                        "total_consumption_kwh": "Consumption (kWh)",
                        "average_power_w": "Average Power (W)",
                        "peak_power_w": "Peak Power (W)",
                        "reading_count": "Reading Count",
                        "usage_pattern": "Usage Pattern",
                    }
                )

                st.dataframe(
                    pattern_df,
                    use_container_width=True,
                    hide_index=True,
                )

                if not pattern_df.empty:
                    fig = px.bar(
                        pattern_df,
                        x="Date",
                        y="Consumption (kWh)",
                        color="Usage Pattern",
                        title="Daily Consumption by Usage Pattern",
                        hover_data=[
                            "Average Power (W)",
                            "Peak Power (W)",
                        ],
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                    )

        elif status in (
            "insufficient_data",
            "insufficient_variation",
        ):
            st.warning(
                "More completed daily readings or greater "
                "variation in consumption may be needed."
            )

    except requests.RequestException as exc:
        st.error(f"Usage pattern analysis failed: {exc}")

        if exc.response is not None:
            st.caption(exc.response.text)

# -------------------------------
# Smart Energy Forecasting
# -------------------------------

st.divider()
st.subheader("Smart Energy Forecasting")

st.write(
    "Estimate tomorrow's electricity consumption using "
    "recent completed daily readings."
)

if st.button("Forecast Tomorrow's Consumption"):
    try:
        response = requests.get(
            f"{API_BASE_URL}/forecast/{device_id}",
            timeout=30,
        )
        response.raise_for_status()
        forecast_data = response.json()

        status = forecast_data.get("status", "unknown")
        st.info(
            forecast_data.get(
                "message",
                "Forecast request completed.",
            )
        )

        if status == "success":
            forecast_col1, forecast_col2 = st.columns(2)

            predicted = forecast_data.get(
                "predicted_consumption_kwh"
            )
            forecast_date = forecast_data.get("forecast_date")

            with forecast_col1:
                if predicted is not None:
                    st.metric(
                        "Predicted Consumption",
                        f"{predicted:.3f} kWh",
                    )

            with forecast_col2:
                st.metric(
                    "Forecast Date",
                    forecast_date or "Not available",
                )

            st.caption(
                f"Based on {forecast_data.get('days_used', 0)} "
                "completed days using the recent daily average."
            )

            st.warning(
                "This is an estimate based on historical usage, "
                "not a guaranteed prediction."
            )

        elif status == "insufficient_data":
            st.warning(
                "Not enough completed daily readings to generate "
                "a reliable forecast. Collect more historical data "
                "and try again."
            )

    except requests.RequestException as exc:
        st.error(f"Energy forecast failed: {exc}")

        if exc.response is not None:
            st.caption(exc.response.text)

# -------------------------------
# Forecast Accuracy Tracking
# -------------------------------

st.divider()
st.subheader("Forecast Accuracy Tracking")

st.write(
    "Compare previous energy forecasts with recorded "
    "daily consumption and evaluate prediction error."
)

if st.button("Check Forecast Accuracy"):
    try:
        response = requests.get(
            f"{API_BASE_URL}/forecast/{device_id}/accuracy",
            timeout=30,
        )
        response.raise_for_status()
        accuracy_data = response.json()

        status = accuracy_data.get("status", "unknown")
        st.info(
            accuracy_data.get(
                "message",
                "Forecast accuracy check completed.",
            )
        )

        if status == "success":
            accuracy_col1, accuracy_col2 = st.columns(2)

            accuracy_col1.metric(
                "Matched Forecast Days",
                accuracy_data.get("matched_days", 0),
            )

            mae = accuracy_data.get("mae_kwh")

            accuracy_col2.metric(
                "Mean Absolute Error (MAE)",
                f"{mae:.3f} kWh" if mae is not None else "N/A",
                help=(
                    "Average absolute difference between predicted "
                    "and actual recorded daily consumption. Lower "
                    "values indicate smaller prediction errors."
                ),
            )

            comparisons = accuracy_data.get("comparisons", [])

            if comparisons:
                accuracy_df = pd.DataFrame(comparisons)

                st.markdown("### Predicted vs Actual Consumption")

                chart_df = accuracy_df.melt(
                    id_vars=["date"],
                    value_vars=[
                        "predicted_consumption_kwh",
                        "actual_consumption_kwh",
                    ],
                    var_name="Consumption Type",
                    value_name="Consumption (kWh)",
                )

                chart_df["Consumption Type"] = chart_df[
                    "Consumption Type"
                ].map(
                    {
                        "predicted_consumption_kwh": "Predicted",
                        "actual_consumption_kwh": "Actual",
                    }
                )

                fig = px.bar(
                    chart_df,
                    x="date",
                    y="Consumption (kWh)",
                    color="Consumption Type",
                    barmode="group",
                    title="Forecast vs Actual Daily Consumption",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

                display_df = accuracy_df.rename(
                    columns={
                        "date": "Date",
                        "predicted_consumption_kwh": "Predicted (kWh)",
                        "actual_consumption_kwh": "Actual (kWh)",
                        "absolute_error_kwh": "Absolute Error (kWh)",
                    }
                )

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                )

        elif status == "insufficient_data":
            st.warning(
                "Accuracy is not available yet. A completed "
                "forecast date must have matching recorded "
                "actual consumption."
            )

    except requests.RequestException as exc:
        st.error(f"Forecast accuracy check failed: {exc}")

        if exc.response is not None:
            st.caption(exc.response.text)




