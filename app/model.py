import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

def _predict_values(train: np.ndarray, horizon: int, method: str) -> np.ndarray:
    if len(train) == 0:
        raise ValueError("Training series cannot be empty")
    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    if method == "naive":
        return np.repeat(float(train[-1]), horizon)
    if method == "moving_average":
        return np.repeat(float(np.mean(train[-min(7, len(train)):])), horizon)
    if method == "linear_trend":
        x = np.arange(len(train)).reshape(-1, 1)
        model = LinearRegression().fit(x, train.astype(float))
        future_x = np.arange(len(train), len(train) + horizon).reshape(-1, 1)
        return np.maximum(model.predict(future_x), 0)
    raise ValueError(f"Unknown model: {method}")

def compare_models(series: pd.Series, test_size: int = 7) -> dict:
    values = series.astype(float).to_numpy()
    if len(values) < test_size + 3:
        test_size = max(1, len(values) // 4)
    if len(values) <= test_size:
        raise ValueError("Not enough observations for a chronological holdout")
    train, actual = values[:-test_size], values[-test_size:]
    results = {}
    for method in ("naive", "moving_average", "linear_trend"):
        pred = _predict_values(train, len(actual), method)
        results[method] = {
            "mae": float(mean_absolute_error(actual, pred)),
            "predictions": pred.tolist(),
        }
    best = min(results, key=lambda key: results[key]["mae"])
    return {"best_model": best, "models": results, "train_size": len(train), "test_size": len(actual)}

def fit_and_save(df: pd.DataFrame, model_path: str | Path, metrics_path: str | Path) -> dict:
    # Evaluate every country and the aggregate series; choose a global method by mean country MAE.
    country_results = {}
    for country, part in df.groupby("country"):
        daily = part.groupby("date")["sales"].sum().sort_index().asfreq("D", fill_value=0)
        country_results[country] = compare_models(daily)
    aggregate = df.groupby("date")["sales"].sum().sort_index().asfreq("D", fill_value=0)
    aggregate_results = compare_models(aggregate)
    mean_scores = {
        name: float(np.mean([r["models"][name]["mae"] for r in country_results.values()]))
        for name in ("naive", "moving_average", "linear_trend")
    }
    best = min(mean_scores, key=mean_scores.get)
    payload = {"best_model": best, "country_scores": mean_scores, "aggregate_scores": aggregate_results["models"], "countries": sorted(df["country"].unique().tolist())}
    model_path, metrics_path = Path(model_path), Path(metrics_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    metrics_path.write_text(json.dumps({"country_evaluations": country_results, "aggregate_evaluation": aggregate_results, "mean_country_mae": mean_scores}, indent=2), encoding="utf-8")
    return payload

def forecast(series: pd.Series, horizon: int, method: str) -> list[float]:
    return [float(x) for x in _predict_values(series.astype(float).to_numpy(), horizon, method)]
