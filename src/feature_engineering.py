import pandas as pd
import numpy as np
from .config import FORWARD_WINDOWS
from .data_cleaner import parse_numeric_value


def add_gold_features(gold: pd.DataFrame) -> pd.DataFrame:
    """Add returns, calendar fields, moving averages, volatility, and regimes."""
    gold = gold.copy().sort_values("date").reset_index(drop=True)

    gold["return_1d"] = gold["close"].pct_change() * 100

    for window in FORWARD_WINDOWS:
        gold[f"return_next_{window}d"] = (gold["close"].shift(-window) / gold["close"] - 1) * 100

    gold["high_low_range_pct"] = ((gold["high"] - gold["low"]) / gold["close"]) * 100
    gold["weekday"] = gold["date"].dt.day_name()
    gold["month"] = gold["date"].dt.month_name()
    gold["month_num"] = gold["date"].dt.month
    gold["year"] = gold["date"].dt.year
    gold["quarter"] = gold["date"].dt.quarter

    gold["rolling_20d_volatility"] = gold["return_1d"].rolling(20).std()
    gold["ma_50"] = gold["close"].rolling(50).mean()
    gold["ma_200"] = gold["close"].rolling(200).mean()

    gold["trend_regime"] = np.where(
        gold["close"] >= gold["ma_200"],
        "Above 200D MA",
        "Below 200D MA"
    )
    gold.loc[gold["ma_200"].isna(), "trend_regime"] = "Not available"

    vol = gold["rolling_20d_volatility"]
    q1, q2 = vol.quantile(0.33), vol.quantile(0.66)
    conditions = [vol <= q1, (vol > q1) & (vol <= q2), vol > q2]
    choices = ["Low volatility", "Medium volatility", "High volatility"]
    gold["volatility_regime"] = np.select(conditions, choices, default="Not available")

    return gold


def add_event_features(events: pd.DataFrame) -> pd.DataFrame:
    """Calculate surprise and classify event result."""
    events = events.copy()

    events["actual_num"] = events["actual"].apply(parse_numeric_value)
    events["forecast_num"] = events["forecast"].apply(parse_numeric_value)
    events["previous_num"] = events["previous"].apply(parse_numeric_value)

    events["surprise"] = events["actual_num"] - events["forecast_num"]

    def classify_surprise(row):
        if pd.isna(row["actual_num"]) or pd.isna(row["forecast_num"]):
            return "Not available"
        if row["actual_num"] > row["forecast_num"]:
            return "Above forecast"
        if row["actual_num"] < row["forecast_num"]:
            return "Below forecast"
        return "In line"

    events["surprise_direction"] = events.apply(classify_surprise, axis=1)

    def classify_event_result(row):
        name = str(row["event_name"]).lower()
        direction = row["surprise_direction"]

        if "cpi" in name or "inflation" in name or "pce" in name:
            if direction == "Above forecast":
                return "Hot inflation"
            if direction == "Below forecast":
                return "Cool inflation"
            if direction == "In line":
                return "Inflation in line"

        if "non-farm" in name or "nonfarm" in name or "nfp" in name or "payroll" in name:
            if direction == "Above forecast":
                return "Strong labour market"
            if direction == "Below forecast":
                return "Weak labour market"
            if direction == "In line":
                return "Labour market in line"

        if "fomc" in name or "fed rate" in name or "interest rate" in name or "rate decision" in name:
            if pd.notna(row["actual_num"]) and pd.notna(row["previous_num"]):
                if row["actual_num"] > row["previous_num"]:
                    return "Rate hike"
                if row["actual_num"] < row["previous_num"]:
                    return "Rate cut"
                return "Rate hold"
            return "FOMC/Rate event"

        return direction

    events["event_result"] = events.apply(classify_event_result, axis=1)
    return events
