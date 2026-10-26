import numpy as np
import pandas as pd
import pytest
from app.model import compare_models, forecast

def test_model_comparison_returns_known_candidates():
    result = compare_models(pd.Series(np.arange(1, 31, dtype=float)), test_size=5)
    assert result["best_model"] in {"naive", "moving_average", "linear_trend"}
    assert set(result["models"]) == {"naive", "moving_average", "linear_trend"}
    assert all(v["mae"] >= 0 for v in result["models"].values())

def test_forecast_length_and_nonnegative_trend():
    predictions = forecast(pd.Series([1, 2, 3, 4, 5]), 4, "linear_trend")
    assert len(predictions) == 4
    assert all(p >= 0 for p in predictions)

def test_invalid_horizon_fails():
    with pytest.raises(ValueError):
        forecast(pd.Series([1, 2, 3]), 0, "naive")
