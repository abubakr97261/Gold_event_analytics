import pandas as pd


def classify_change(actual, previous):
    if pd.isna(actual) or pd.isna(previous):
        return "Not available"

    if actual > previous:
        return "Higher than previous"
    elif actual < previous:
        return "Lower than previous"
    else:
        return "Unchanged"


def build_events_from_fred_series(
    df,
    value_column,
    event_name,
    category,
    country="United States",
    impact="High"
):
    """
    Convert a FRED macro time series into an economic_events-style table.

    This uses actual-vs-previous as a free proxy for surprise.
    It does not contain market forecast/consensus.
    """

    data = df.copy()
    data = data.sort_values("date")

    data["previous"] = data[value_column].shift(1)
    data["actual"] = data[value_column]
    data["forecast"] = None
    data["surprise"] = data["actual"] - data["previous"]
    data["surprise_direction"] = data.apply(
        lambda row: classify_change(row["actual"], row["previous"]),
        axis=1
    )

    events = pd.DataFrame({
        "event_date": data["date"],
        "event_time": "08:30:00",
        "country": country,
        "event_name": event_name,
        "category": category,
        "actual": data["actual"],
        "forecast": data["forecast"],
        "previous": data["previous"],
        "surprise": data["surprise"],
        "surprise_direction": data["surprise_direction"],
        "impact": impact
    })

    return events.dropna(subset=["actual"])