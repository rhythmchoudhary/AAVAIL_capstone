import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = Path(os.getenv("DATA_PATH", ROOT / "data" / "sample_sales.csv"))
MODEL_PATH = Path(os.getenv("MODEL_PATH", ROOT / "artifacts" / "model.json"))
LOG_PATH = Path(os.getenv("LOG_PATH", ROOT / "logs" / "api.jsonl"))
METRICS_PATH = ROOT / "artifacts" / "metrics.json"
