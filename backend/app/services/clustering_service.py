
from datetime import date, datetime

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models import Reading


def get_usage_patterns(
    db: Session,
    device_id: int,
    min_days: int = 5,
) -> dict:
    """Group completed daily consumption records into usage patterns."""

    if device_id <= 0:
        raise ValueError("device_id must be greater than zero")

    if min_days < 3:
        raise ValueError("min_days must be at least 3")

    today = date.today().isoformat()

    statement = (
        select(
            func.date(Reading.recorded_at).label("date"),
            func.coalesce(
                func.sum(Reading.energy_kwh), 0.0
            ).label("total_energy"),
            func.avg(Reading.power_w).label("average_power"),
            func.max(Reading.power_w).label("peak_power"),
            func.count(Reading.id).label("reading_count"),
        )
        .where(
            Reading.device_id == device_id,
            func.date(Reading.recorded_at) < today,
        )
        .group_by(func.date(Reading.recorded_at))
        .order_by(func.date(Reading.recorded_at))
    )

    rows = db.execute(statement).all()

    daily_data = [
        {
            "date": str(row.date),
            "total_consumption_kwh": float(row.total_energy or 0.0),
            "average_power_w": (
                float(row.average_power)
                if row.average_power is not None
                else 0.0
            ),
            "peak_power_w": (
                float(row.peak_power)
                if row.peak_power is not None
                else 0.0
            ),
            "reading_count": int(row.reading_count),
        }
        for row in rows
    ]

    if len(daily_data) < min_days:
        return {
            "device_id": device_id,
            "status": "insufficient_data",
            "message": (
                f"At least {min_days} completed days are required "
                "for clustering."
            ),
            "days_available": len(daily_data),
            "clusters": [],
            "daily_patterns": [],
        }

    features = np.array(
        [
            [
                item["total_consumption_kwh"],
                item["average_power_w"],
                item["peak_power_w"],
            ]
            for item in daily_data
        ],
        dtype=float,
    )

    if not np.isfinite(features).all():
        raise ValueError("Consumption data contains invalid numeric values")

    if np.any(features < 0):
        raise ValueError("Consumption features cannot be negative")

    unique_features = np.unique(features, axis=0)
    cluster_count = min(3, len(unique_features))

    if cluster_count < 2:
        return {
            "device_id": device_id,
            "status": "insufficient_variation",
            "message": (
                "Different usage patterns cannot be identified because "
                "the available daily readings are too similar."
            ),
            "days_available": len(daily_data),
            "clusters": [],
            "daily_patterns": [],
        }

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    model = KMeans(
        n_clusters=cluster_count,
        random_state=42,
        n_init=10,
    )
    labels = model.fit_predict(scaled_features)

    # Order clusters by average daily energy consumption.
    cluster_energy = {
        cluster_id: float(
            np.mean(
                features[labels == cluster_id, 0]
            )
        )
        for cluster_id in range(cluster_count)
    }

    ordered_ids = sorted(
        cluster_energy,
        key=cluster_energy.get,
    )

    label_names = {}
    for rank, cluster_id in enumerate(ordered_ids):
        if cluster_count == 2:
            name = "Low" if rank == 0 else "High"
        else:
            name = ["Low", "Medium", "High"][rank]

        label_names[cluster_id] = name

    for item, cluster_id in zip(daily_data, labels):
        item["cluster"] = int(cluster_id)
        item["usage_pattern"] = label_names[int(cluster_id)]

    clusters = []
    for cluster_id in ordered_ids:
        members = features[labels == cluster_id]
        clusters.append(
            {
                "cluster": int(cluster_id),
                "usage_pattern": label_names[cluster_id],
                "days_count": int(len(members)),
                "average_daily_consumption_kwh": round(
                    float(np.mean(members[:, 0])), 3
                ),
                "average_power_w": round(
                    float(np.mean(members[:, 1])), 2
                ),
                "peak_power_w": round(
                    float(np.mean(members[:, 2])), 2
                ),
            }
        )

    return {
        "device_id": device_id,
        "status": "success",
        "message": (
            "Preliminary usage patterns generated from completed days. "
            "More historical data may improve their reliability."
        ),
        "days_available": len(daily_data),
        "clusters": clusters,
        "daily_patterns": daily_data,
    }
