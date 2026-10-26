import json
import logging
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app import main
from app.logging_utils import build_logger

@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "sales.csv"
    rows = []
    for country, multiplier in [("India", 2), ("Canada", 1)]:
        for day in pd.date_range("2025-01-01", periods=20, freq="D"):
            rows.append({"date": day.date().isoformat(), "country": country, "sales": multiplier * (10 + day.day)})
    pd.DataFrame(rows).to_csv(path, index=False)
    return path

@pytest.fixture
def client(tmp_path, sample_csv, monkeypatch):
    model_path = tmp_path / "model.json"
    model_path.write_text(json.dumps({"best_model": "naive", "countries": ["India", "Canada"]}))
    log_path = tmp_path / "test-api.jsonl"
    monkeypatch.setattr(main, "DATA_PATH", sample_csv)
    monkeypatch.setattr(main, "MODEL_PATH", model_path)
    monkeypatch.setattr(main, "LOG_PATH", log_path)
    monkeypatch.setattr(main, "logger", build_logger(log_path))
    monkeypatch.setattr(main, "REQUEST_COUNT", 0)
    monkeypatch.setattr(main, "REQUEST_LATENCIES_MS", __import__("collections").deque(maxlen=1000))
    return TestClient(main.app)
