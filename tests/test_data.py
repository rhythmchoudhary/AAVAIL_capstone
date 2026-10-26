import pandas as pd
from app.data import ingest_sales

def test_ingestion_cleans_and_aggregates(tmp_path):
    p = tmp_path / "input.csv"
    pd.DataFrame([
        {"date": "2025-01-01", "country": " India ", "sales": 10},
        {"date": "2025-01-01", "country": "India", "sales": 5},
        {"date": "bad-date", "country": "India", "sales": 3},
        {"date": "2025-01-02", "country": "Canada", "sales": -4},
    ]).to_csv(p, index=False)
    out = ingest_sales(p)
    assert len(out) == 1
    assert out.iloc[0]["country"] == "India"
    assert out.iloc[0]["sales"] == 15
