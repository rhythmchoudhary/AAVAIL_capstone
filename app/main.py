import json
import time
from collections import deque
from datetime import date, timedelta
from fastapi import FastAPI, HTTPException, Query
import pandas as pd
from app.config import DATA_PATH, MODEL_PATH, LOG_PATH
from app.data import ingest_sales
from app.model import forecast
from app.logging_utils import build_logger, log_event

app = FastAPI(title="Country Demand Forecast API", version="1.0.0")
logger = build_logger(LOG_PATH)
REQUEST_LATENCIES_MS = deque(maxlen=1000)
REQUEST_COUNT = 0

def _load_model():
    if not MODEL_PATH.exists():
        raise RuntimeError("Model artifact not found. Run `python scripts/run_pipeline.py` first.")
    return json.loads(MODEL_PATH.read_text(encoding="utf-8"))

@app.get("/health")
def health():
    return {"status": "ok", "model_ready": MODEL_PATH.exists()}

@app.get("/metrics")
def metrics():
    values = list(REQUEST_LATENCIES_MS)
    return {
        "request_count": REQUEST_COUNT,
        "latency_ms_mean": round(sum(values) / len(values), 3) if values else 0.0,
        "latency_ms_max": round(max(values), 3) if values else 0.0,
        "latency_samples": len(values),
    }

@app.get("/predict")
def predict(country: str | None = Query(default=None), horizon: int = Query(default=7, ge=1, le=30)):
    global REQUEST_COUNT
    started = time.perf_counter()
    try:
        df = ingest_sales(DATA_PATH)
        model_info = _load_model()
        if country:
            subset = df[df["country"].str.casefold() == country.casefold()]
            if subset.empty:
                raise HTTPException(status_code=404, detail=f"Country not found: {country}")
            series = subset.groupby("date")["sales"].sum().sort_index().asfreq("D", fill_value=0)
            method = model_info["best_model"]
            predictions = forecast(series, horizon, method)
            result = {"scope": "country", "country": country, "model": method, "horizon": horizon, "predictions": predictions}
        else:
            series = df.groupby("date")["sales"].sum().sort_index().asfreq("D", fill_value=0)
            method = model_info["best_model"]
            predictions = forecast(series, horizon, method)
            result = {"scope": "all_countries", "country": None, "model": method, "horizon": horizon, "predictions": predictions}
        REQUEST_COUNT += 1
        latency = (time.perf_counter() - started) * 1000
        REQUEST_LATENCIES_MS.append(latency)
        log_event(logger, "prediction_success", country=country, horizon=horizon, latency_ms=round(latency, 3), scope=result["scope"])
        return result
    except HTTPException as exc:
        log_event(logger, "prediction_error", country=country, horizon=horizon, status_code=exc.status_code)
        raise
    except Exception as exc:
        log_event(logger, "prediction_error", country=country, horizon=horizon, error_type=type(exc).__name__)
        raise HTTPException(status_code=500, detail="Prediction failed; check server logs.") from exc
