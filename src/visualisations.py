import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from .config import CHARTS_DIR


def _save_fig(filename: str):
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    path = CHARTS_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_gold_price(gold: pd.DataFrame):
    plt.figure(figsize=(12, 6))
    plt.plot(gold["date"], gold["close"])
    plt.title("Gold Close Price")
    plt.xlabel("Date")
    plt.ylabel("Close")
    return _save_fig("gold_price_line_chart.png")


def plot_average_return_by_month(monthly_summary: pd.DataFrame):
    plt.figure(figsize=(12, 6))
    plt.bar(monthly_summary["month"], monthly_summary["average_monthly_return"])
    plt.title("Average Monthly Gold Return")
    plt.xlabel("Month")
    plt.ylabel("Average monthly return (%)")
    plt.xticks(rotation=45)
    return _save_fig("average_return_by_month.png")


def plot_weekday_performance(weekday_summary: pd.DataFrame):
    plt.figure(figsize=(10, 5))
    plt.bar(weekday_summary["weekday"], weekday_summary["average_daily_return"])
    plt.title("Average Gold Daily Return by Weekday")
    plt.xlabel("Weekday")
    plt.ylabel("Average daily return (%)")
    return _save_fig("weekday_performance.png")


def plot_event_reaction_bar(event_summary: pd.DataFrame):
    if event_summary.empty:
        return None
    top = event_summary.sort_values("average_return_10d", ascending=False).head(15)
    plt.figure(figsize=(12, 7))
    plt.barh(top["event_name"], top["average_return_10d"])
    plt.title("Top Event Types by Average 10D Gold Return")
    plt.xlabel("Average 10D return (%)")
    plt.ylabel("Event")
    return _save_fig("event_reaction_bar.png")


def plot_event_category_comparison(reactions: pd.DataFrame, keyword: str, filename: str):
    if reactions.empty:
        return None
    data = reactions[reactions["event_name"].str.contains(keyword, case=False, na=False)]
    if data.empty:
        return None
    grouped = data.groupby("surprise_direction")["return_5d"].mean().reset_index()
    plt.figure(figsize=(8, 5))
    plt.bar(grouped["surprise_direction"], grouped["return_5d"])
    plt.title(f"{keyword.upper()} Average 5D Gold Reaction")
    plt.xlabel("Surprise direction")
    plt.ylabel("Average 5D return (%)")
    plt.xticks(rotation=30)
    return _save_fig(filename)


def plot_return_distribution(reactions: pd.DataFrame):
    if reactions.empty:
        return None
    plt.figure(figsize=(10, 5))
    plt.hist(reactions["return_5d"].dropna(), bins=30)
    plt.title("Distribution of 5D Post-Event Gold Returns")
    plt.xlabel("5D return (%)")
    plt.ylabel("Frequency")
    return _save_fig("distribution_post_event_returns.png")


def plot_event_study_line(reactions: pd.DataFrame):
    if reactions.empty:
        return None
    windows = ["return_0d", "return_1d", "return_3d", "return_5d", "return_10d", "return_20d"]
    labels = ["0D", "1D", "3D", "5D", "10D", "20D"]
    avg = [reactions[col].mean() for col in windows]
    plt.figure(figsize=(10, 5))
    plt.plot(labels, avg, marker="o")
    plt.title("Average Gold Event Study Return")
    plt.xlabel("Window")
    plt.ylabel("Average return (%)")
    return _save_fig("event_study_line_chart.png")


def plot_monthly_return_heatmap(gold: pd.DataFrame):
    monthly = (
        gold.set_index("date")["close"]
        .resample("ME")
        .last()
        .pct_change()
        .mul(100)
        .reset_index(name="monthly_return")
    )
    monthly["year"] = monthly["date"].dt.year
    monthly["month"] = monthly["date"].dt.month

    pivot = monthly.pivot(index="year", columns="month", values="monthly_return")
    if pivot.empty:
        return None

    plt.figure(figsize=(12, 8))
    plt.imshow(pivot, aspect="auto")
    plt.title("Monthly Gold Return Heatmap")
    plt.xlabel("Month")
    plt.ylabel("Year")
    plt.xticks(ticks=range(12), labels=list(range(1, 13)))
    plt.yticks(ticks=range(len(pivot.index)), labels=pivot.index)
    plt.colorbar(label="Monthly return (%)")
    return _save_fig("monthly_return_heatmap.png")


def create_all_charts(gold, monthly_summary, weekday_summary, event_summary, reactions):
    paths = []
    for chart_func in [
        lambda: plot_gold_price(gold),
        lambda: plot_monthly_return_heatmap(gold),
        lambda: plot_average_return_by_month(monthly_summary),
        lambda: plot_weekday_performance(weekday_summary),
        lambda: plot_event_reaction_bar(event_summary),
        lambda: plot_event_category_comparison(reactions, "cpi", "cpi_reaction_comparison.png"),
        lambda: plot_event_category_comparison(reactions, "payroll|nfp|non-farm|nonfarm", "nfp_reaction_comparison.png"),
        lambda: plot_event_category_comparison(reactions, "fomc|rate", "fomc_reaction_comparison.png"),
        lambda: plot_event_study_line(reactions),
        lambda: plot_return_distribution(reactions)
    ]:
        try:
            path = chart_func()
            if path:
                paths.append(path)
        except Exception as exc:
            print(f"Chart skipped due to error: {exc}")
    return paths
