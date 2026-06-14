import pandas as pd
import numpy as np


MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def _win_rate(series: pd.Series) -> float:
    series = series.dropna()
    if len(series) == 0:
        return np.nan
    return (series > 0).mean() * 100


def monthly_seasonality(gold: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly returns and seasonality summary."""
    monthly = (
        gold.set_index("date")["close"]
        .resample("ME")
        .last()
        .pct_change()
        .mul(100)
        .reset_index(name="monthly_return")
    )
    monthly["month"] = monthly["date"].dt.month_name()
    monthly["month_num"] = monthly["date"].dt.month
    monthly["year"] = monthly["date"].dt.year

    summary = monthly.groupby(["month_num", "month"]).agg(
        average_monthly_return=("monthly_return", "mean"),
        median_monthly_return=("monthly_return", "median"),
        win_rate=("monthly_return", _win_rate),
        number_of_observations=("monthly_return", "count"),
    ).reset_index()

    best = monthly.loc[monthly.groupby("month_num")["monthly_return"].idxmax().dropna()]
    worst = monthly.loc[monthly.groupby("month_num")["monthly_return"].idxmin().dropna()]
    summary = summary.merge(
        best[["month_num", "year"]].rename(columns={"year": "best_year"}),
        on="month_num",
        how="left"
    ).merge(
        worst[["month_num", "year"]].rename(columns={"year": "worst_year"}),
        on="month_num",
        how="left"
    )
    return summary.sort_values("month_num")


def weekday_performance(gold: pd.DataFrame) -> pd.DataFrame:
    summary = gold.groupby("weekday").agg(
        average_daily_return=("return_1d", "mean"),
        median_daily_return=("return_1d", "median"),
        win_rate=("return_1d", _win_rate),
        average_high_low_range=("high_low_range_pct", "mean"),
        number_of_observations=("return_1d", "count")
    ).reset_index()

    summary["weekday_order"] = summary["weekday"].map({d: i for i, d in enumerate(WEEKDAY_ORDER)})
    return summary.sort_values("weekday_order").drop(columns=["weekday_order"])


def event_performance(reactions: pd.DataFrame) -> pd.DataFrame:
    if reactions.empty:
        return pd.DataFrame()

    summary = reactions.groupby(["event_name", "category"]).agg(
        average_return_0d=("return_0d", "mean"),
        average_return_1d=("return_1d", "mean"),
        average_return_3d=("return_3d", "mean"),
        average_return_5d=("return_5d", "mean"),
        average_return_10d=("return_10d", "mean"),
        average_return_20d=("return_20d", "mean"),
        win_rate_1d=("return_1d", _win_rate),
        win_rate_5d=("return_5d", _win_rate),
        win_rate_10d=("return_10d", _win_rate),
        number_of_events=("event_id", "count")
    ).reset_index()

    return summary.sort_values("number_of_events", ascending=False)


def event_surprise_performance(reactions: pd.DataFrame) -> pd.DataFrame:
    if reactions.empty:
        return pd.DataFrame()

    summary = reactions.groupby(["event_name", "surprise_direction"]).agg(
        average_return_1d=("return_1d", "mean"),
        average_return_5d=("return_5d", "mean"),
        average_return_10d=("return_10d", "mean"),
        win_rate_1d=("return_1d", _win_rate),
        win_rate_5d=("return_5d", _win_rate),
        win_rate_10d=("return_10d", _win_rate),
        count=("event_id", "count")
    ).reset_index()

    return summary.sort_values(["event_name", "count"], ascending=[True, False])


def best_worst_event_reactions(reactions: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    if reactions.empty:
        return pd.DataFrame()

    cols = [
        "event_date", "event_name", "category", "surprise_direction",
        "return_1d", "return_5d", "return_10d"
    ]
    best = reactions.nlargest(top_n, "return_10d")[cols].copy()
    best["rank_type"] = "Best 10D reactions"
    worst = reactions.nsmallest(top_n, "return_10d")[cols].copy()
    worst["rank_type"] = "Worst 10D reactions"
    return pd.concat([best, worst], ignore_index=True)
