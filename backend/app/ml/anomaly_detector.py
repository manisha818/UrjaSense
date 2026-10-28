from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import IsolationForest


FEATURE_COLUMNS = ("voltage", "current", "power_w")


@dataclass(frozen=True)
class AnomalyResult:
    is_anomaly: bool
    anomaly_score: float
    label: int


class ElectricityAnomalyDetector:
    """Detect unusual electricity readings against a learned baseline."""

    def __init__(
        self,
        contamination: float = 0.05,
        random_state: int = 42,
    ) -> None:
        if not 0 < contamination <= 0.5:
            raise ValueError(
                "contamination must be greater than 0 and at most 0.5"
            )

        self.contamination = contamination
        self.random_state = random_state
        self._model = None
        self._lower_bounds = None
        self._upper_bounds = None
        self._feature_scales = None

    @staticmethod
    def _validate_rows(
        readings: list[dict],
        minimum_count: int,
    ) -> np.ndarray:
        if not isinstance(readings, list):
            raise ValueError("readings must be a list")

        if len(readings) < minimum_count:
            raise ValueError(
                f"At least {minimum_count} readings are required"
            )

        rows = []

        for index, reading in enumerate(readings):
            if not isinstance(reading, dict):
                raise ValueError(
                    f"Reading at index {index} must be a dictionary"
                )

            values = []

            for feature in FEATURE_COLUMNS:
                value = reading.get(feature)

                if value is None or isinstance(value, bool):
                    raise ValueError(
                        f"Reading {index}: {feature} must be a finite number"
                    )

                try:
                    number = float(value)
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Reading {index}: {feature} must be a finite number"
                    ) from exc

                if not np.isfinite(number):
                    raise ValueError(
                        f"Reading {index}: {feature} must be a finite number"
                    )

                if number < 0:
                    raise ValueError(
                        f"Reading {index}: {feature} cannot be negative"
                    )

                values.append(number)

            rows.append(values)

        return np.asarray(rows, dtype=float)

    def fit(self, readings: list[dict]) -> "ElectricityAnomalyDetector":
        """Learn typical feature ranges and patterns from historical data."""
        data = self._validate_rows(readings, minimum_count=5)

        q1 = np.percentile(data, 25, axis=0)
        q3 = np.percentile(data, 75, axis=0)
        iqr = q3 - q1

        # A small nonzero floor also handles features with nearly constant values.
        floor = np.maximum(np.abs(np.median(data, axis=0)) * 0.01, 0.01)
        spread = np.maximum(iqr, floor)

        self._lower_bounds = q1 - 3.0 * spread
        self._upper_bounds = q3 + 3.0 * spread

        self._feature_scales = np.maximum(
            np.std(data, axis=0),
            floor,
        )

        self._model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
        )
        self._model.fit(data)

        return self

    def predict(self, reading: dict) -> AnomalyResult:
        """Classify a reading after fitting the model."""
        if self._model is None:
            raise RuntimeError(
                "Model is not fitted. Call fit() with historical readings first."
            )

        data = self._validate_rows([reading], minimum_count=1)

        forest_label = int(self._model.predict(data)[0])
        forest_score = float(self._model.decision_function(data)[0])

        outside_bounds = bool(
            np.any(data[0] < self._lower_bounds)
            or np.any(data[0] > self._upper_bounds)
        )

        is_anomaly = forest_label == -1 or outside_bounds

        # Lower scores indicate more unusual forest predictions.
        score = forest_score

        if outside_bounds:
            distance = np.maximum(
                self._lower_bounds - data[0],
                data[0] - self._upper_bounds,
            )
            distance = np.maximum(distance, 0.0)
            normalized_distance = float(
                np.max(distance / self._feature_scales)
            )
            score = min(score, -normalized_distance)

        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_score=round(score, 6),
            label=-1 if is_anomaly else 1,
        )
