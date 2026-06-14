import pandas as pd
from pathlib import Path
from .config import POWERBI_EXPORT_DIR


def _export(df: pd.DataFrame, filename: str):
    POWERBI_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%d")
    path = POWERBI_EXPORT_DIR / filename
    out.to_csv(path, index=False)
    return path


def export_all(
    gold,
    events,
    reactions,
    monthly_summary,
    weekday_summary,
    event_summary,
    event_surprise_summary,
    best_worst_summary
):
    paths = []
    paths.append(_export(gold, "gold_prices_clean.csv"))
    paths.append(_export(events, "economic_events_clean.csv"))
    paths.append(_export(reactions, "gold_event_reactions.csv"))
    paths.append(_export(monthly_summary, "monthly_seasonality_summary.csv"))
    paths.append(_export(weekday_summary, "weekday_performance_summary.csv"))
    paths.append(_export(event_summary, "event_performance_summary.csv"))
    paths.append(_export(event_surprise_summary, "event_surprise_summary.csv"))
    paths.append(_export(best_worst_summary, "best_worst_event_reactions.csv"))
    return paths
