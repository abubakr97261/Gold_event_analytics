import pandas as pd
import numpy as np


def _standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        str(c).strip().lower().replace(" ", "_").replace("-", "_")
        for c in df.columns
    ]
    return df


import pandas as pd


def clean_gold_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean gold OHLCV data.
    Expected final columns:
    date, open, high, low, close, volume
    """

    if df is None or df.empty:
        print("WARNING: gold price input is empty.")
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])

    out = df.copy()

    out.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in out.columns
    ]

    rename_map = {
        "datetime": "date",
        "price": "date",
        "adj_close": "adj_close",
    }

    out = out.rename(columns=rename_map)

    required_cols = ["date", "open", "high", "low", "close", "volume"]

    missing = [col for col in required_cols if col not in out.columns]
    if missing:
        raise ValueError(
            f"Gold data is missing required columns: {missing}. "
            f"Available columns: {list(out.columns)}"
        )

    out = out[required_cols].copy()

    out["date"] = pd.to_datetime(out["date"], errors="coerce")

    for col in ["open", "high", "low", "close", "volume"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    before = len(out)

    out = out.dropna(subset=["date", "close"])
    out = out.sort_values("date")
    out = out.drop_duplicates(subset=["date"])

    after = len(out)

    print(f"Gold rows before cleaning: {before}")
    print(f"Gold rows after cleaning: {after}")

    return out


def clean_economic_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean economic events data.
    """

    if df is None or df.empty:
        print("WARNING: economic events input is empty.")
        return pd.DataFrame(columns=[
            "event_id",
            "event_date",
            "event_time",
            "country",
            "event_name",
            "category",
            "actual",
            "forecast",
            "previous",
            "surprise",
            "surprise_direction",
            "impact",
        ])

    out = df.copy()

    out.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in out.columns
    ]

    if "date" in out.columns and "event_date" not in out.columns:
        out = out.rename(columns={"date": "event_date"})

    required_cols = [
        "event_date",
        "event_time",
        "country",
        "event_name",
        "category",
        "actual",
        "forecast",
        "previous",
        "surprise",
        "surprise_direction",
        "impact",
    ]

    for col in required_cols:
        if col not in out.columns:
            out[col] = None

    out["event_date"] = pd.to_datetime(out["event_date"], errors="coerce")

    for col in ["actual", "forecast", "previous", "surprise"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out = out.dropna(subset=["event_date"])
    out = out.sort_values("event_date").drop_duplicates()

    if "event_id" not in out.columns:
        out.insert(0, "event_id", range(1, len(out) + 1))

    return out

def clean_economic_events(events: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardise economic calendar/event data."""
    events = _standardise_columns(events)

    required_defaults = {
        "event_date": None,
        "event_time": "",
        "country": "",
        "event_name": "",
        "category": "",
        "actual": np.nan,
        "forecast": np.nan,
        "previous": np.nan,
        "impact": ""
    }

    # Accept a plain "date" column as event_date.
    if "event_date" not in events.columns and "date" in events.columns:
        events = events.rename(columns={"date": "event_date"})

    for col, default in required_defaults.items():
        if col not in events.columns:
            events[col] = default

    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce").dt.normalize()
    events = events.dropna(subset=["event_date"])
    events["event_name"] = events["event_name"].astype(str).str.strip()
    events["category"] = events["category"].astype(str).str.strip()
    events["country"] = events["country"].astype(str).str.strip()
    events["impact"] = events["impact"].astype(str).str.strip()

    events = events.drop_duplicates(
        subset=["event_date", "event_time", "country", "event_name", "category"],
        keep="first"
    ).sort_values(["event_date", "event_name"]).reset_index(drop=True)

    events.insert(0, "event_id", range(1, len(events) + 1))
    return events


def parse_numeric_value(value):
    """Extract a numeric value from calendar fields such as '3.2%', '216K', '5.50'."""
    if pd.isna(value):
        return np.nan
    text = str(value).strip().replace(",", "")
    multiplier = 1.0
    if text.endswith("%"):
        text = text[:-1]
    elif text.upper().endswith("K"):
        text = text[:-1]
        multiplier = 1_000.0
    elif text.upper().endswith("M"):
        text = text[:-1]
        multiplier = 1_000_000.0
    elif text.upper().endswith("B"):
        text = text[:-1]
        multiplier = 1_000_000_000.0
    try:
        return float(text) * multiplier
    except ValueError:
        return np.nan
