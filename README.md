# AI Business Solution: Country-Level Demand Forecasting API

A reproducible capstone demonstrating an end-to-end AI workflow: data ingestion, EDA visualizations, comparison of multiple forecasting baselines/models, a FastAPI prediction service, structured logging, performance monitoring, automated tests, and Docker deployment.

> **Important:** This repository is a complete runnable starter implementation using a clearly labeled synthetic sample dataset. Replace `data/sample_sales.csv` with the course-provided AAVAIL/business dataset and rerun the workflow before claiming results on real data.

## Features
- Ingest CSV sales data with `date`, `country`, and `sales` columns.
- Validate and clean records.
- EDA charts for sales trends and country comparisons.
- Compare naive, 7-day moving-average, and linear-trend models using a chronological holdout.
- Select the model with the lowest MAE.
- FastAPI endpoints for a specific country and all countries combined.
- JSON request logs and basic API performance metrics.
- Unit tests for API, model, and logging.
- One command to run tests.
- Docker image and Docker Compose configuration.
- Test mode writes logs/artifacts to temporary directories; it does not modify production artifacts.

## Quick start (Python 3.11+)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_pipeline.py
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs.

## API examples
Specific country:
```bash
curl "http://127.0.0.1:8000/predict?country=India&horizon=7"
```
All countries combined:
```bash
curl "http://127.0.0.1:8000/predict?horizon=7"
```
Health and metrics:
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/metrics
```

## Run tests
```bash
pytest -q
```
All tests use temporary directories / in-memory test clients for logs and model artifacts. They do not overwrite the normal `artifacts/` or `logs/` directories.

## Pipeline outputs
`python scripts/run_pipeline.py` creates:
- `artifacts/model.json` — selected model settings and evaluation metrics.
- `artifacts/metrics.json` — holdout model comparison.
- `reports/eda_sales_by_country.png`
- `reports/model_comparison.png`

## Docker
```bash
docker compose up --build
```
Then open http://localhost:8000/docs.

## Dataset format
CSV columns:
- `date`: parseable date, e.g. `2025-01-01`
- `country`: country name
- `sales`: numeric non-negative sales

The included synthetic dataset is only for demonstrating the workflow. For a course submission, use the permitted course dataset and document its provenance and any limitations.
