import pandas as pd
import numpy as np
from bisect import bisect_left


REACTION_COLUMNS = [
    "reaction_id",
    "event_id",
    "event_date",
    "matched_gold_date",
    "event_name",
    "category",
    "surprise_direction",
    "gold_close_before",
    "gold_close_event_day",
    "gold_close_after_1d",
    "gold_close_after_3d",
    "gold_close_after_5d",
    "gold_close_after_10d",
    "gold_close_after_20d",
    "return_0d",
    "return_1d",
    "return_3d",
    "return_5d",
    "return_10d",
    "return_20d",
    "max_gain_10d",
    "max_drawdown_10d",
    "direction_1d",
    "direction_5d",
    "direction_10d",
]


def _pct_return(start, end):
    if pd.isna(start) or pd.isna(end) or start == 0:
        return np.nan
    return (end / start - 1) * 100


def _direction(value):
    if pd.isna(value):
        return "Not available"
    if value > 0:
        return "Up"
    if value < 0:
        return "Down"
    return "Flat"


def build_event_reactions(gold: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """
    Match economic events to gold trading dates and calculate forward returns.
    Always returns a DataFrame with valid columns, even if no reactions are created.
    """

    if gold is None or events is None or gold.empty or events.empty:
        return pd.DataFrame(columns=REACTION_COLUMNS)

    gold = gold.copy()
    events = events.copy()

    gold["date"] = pd.to_datetime(gold["date"], errors="coerce")
    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")

    gold["close"] = pd.to_numeric(gold["close"], errors="coerce")

    gold = gold.dropna(subset=["date", "close"])
    events = events.dropna(subset=["event_date"])

    gold = gold.sort_values("date").reset_index(drop=True)
    events = events.sort_values("event_date").reset_index(drop=True)

    if gold.empty or events.empty:
        return pd.DataFrame(columns=REACTION_COLUMNS)

    trading_dates = list(gold["date"])
    records = []

    for i, event in events.iterrows():
        event_date = event["event_date"]

        # Match event to first available trading date >= event date
        idx = bisect_left(trading_dates, event_date)

        # Skip if event is after last gold date or no previous close available
        if idx >= len(gold) or idx == 0:
            continue

        before_close = gold.loc[idx - 1, "close"]
        event_close = gold.loc[idx, "close"]

        def close_after(days):
            target_idx = idx + days
            if target_idx < len(gold):
                return gold.loc[target_idx, "close"]
            return np.nan

        close_1d = close_after(1)
        close_3d = close_after(3)
        close_5d = close_after(5)
        close_10d = close_after(10)
        close_20d = close_after(20)

        return_0d = _pct_return(before_close, event_close)
        return_1d = _pct_return(event_close, close_1d)
        return_3d = _pct_return(event_close, close_3d)
        return_5d = _pct_return(event_close, close_5d)
        return_10d = _pct_return(event_close, close_10d)
        return_20d = _pct_return(event_close, close_20d)

        post_10 = gold.loc[idx:min(idx + 10, len(gold) - 1), "close"]

        if len(post_10) > 0 and pd.notna(event_close) and event_close != 0:
            max_gain_10d = (post_10.max() / event_close - 1) * 100
            max_drawdown_10d = (post_10.min() / event_close - 1) * 100
        else:
            max_gain_10d = np.nan
            max_drawdown_10d = np.nan

        records.append({
            "reaction_id": len(records) + 1,
            "event_id": event.get("event_id", i + 1),
            "event_date": event_date,
            "matched_gold_date": gold.loc[idx, "date"],
            "event_name": event.get("event_name", ""),
            "category": event.get("category", ""),
            "surprise_direction": event.get("surprise_direction", "Not available"),
            "gold_close_before": before_close,
            "gold_close_event_day": event_close,
            "gold_close_after_1d": close_1d,
            "gold_close_after_3d": close_3d,
            "gold_close_after_5d": close_5d,
            "gold_close_after_10d": close_10d,
            "gold_close_after_20d": close_20d,
            "return_0d": return_0d,
            "return_1d": return_1d,
            "return_3d": return_3d,
            "return_5d": return_5d,
            "return_10d": return_10d,
            "return_20d": return_20d,
            "max_gain_10d": max_gain_10d,
            "max_drawdown_10d": max_drawdown_10d,
            "direction_1d": _direction(return_1d),
            "direction_5d": _direction(return_5d),
            "direction_10d": _direction(return_10d),
        })

    return pd.DataFrame(records, columns=REACTION_COLUMNS)