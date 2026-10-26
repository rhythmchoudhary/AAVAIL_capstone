from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from app.config import ROOT, DATA_PATH, MODEL_PATH, METRICS_PATH
from app.data import ingest_sales
from app.model import fit_and_save

def main():
    df = ingest_sales(DATA_PATH)
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "artifacts").mkdir(exist_ok=True)
    # EDA: daily sales by country
    fig, ax = plt.subplots(figsize=(10, 5))
    for country, part in df.groupby("country"):
        daily = part.groupby("date")["sales"].sum().sort_index()
        ax.plot(daily.index, daily.values, label=country)
    ax.set_title("Daily Sales by Country")
    ax.set_xlabel("Date"); ax.set_ylabel("Sales")
    ax.legend(); fig.tight_layout()
    fig.savefig(ROOT / "reports" / "eda_sales_by_country.png", dpi=140); plt.close(fig)
    result = fit_and_save(df, MODEL_PATH, METRICS_PATH)
    # Visual comparison of model MAE on aggregate series
    agg_scores = result["aggregate_scores"]
    names = list(agg_scores)
    vals = [agg_scores[n]["mae"] for n in names]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(names, vals)
    ax.set_title("Model Comparison on Chronological Holdout (lower MAE is better)")
    ax.set_ylabel("Mean Absolute Error")
    fig.tight_layout()
    fig.savefig(ROOT / "reports" / "model_comparison.png", dpi=140); plt.close(fig)
    print(json.dumps({"selected_model": result["best_model"], "country_scores": result["country_scores"]}, indent=2))

if __name__ == "__main__":
    main()
