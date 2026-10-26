from pathlib import Path
import pandas as pd

REQUIRED = {"date", "country", "sales"}

def ingest_sales(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    df = df[["date", "country", "sales"]].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["country"] = df["country"].astype(str).str.strip()
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df = df.dropna(subset=["date", "country", "sales"])
    df = df[(df["country"] != "") & (df["sales"] >= 0)]
    df = df.groupby(["date", "country"], as_index=False)["sales"].sum()
    return df.sort_values(["country", "date"]).reset_index(drop=True)
