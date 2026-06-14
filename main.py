# from src.data_loader import load_gold_prices, load_economic_events, load_from_yfinance
# from src.data_cleaner import clean_gold_prices, clean_economic_events
# from src.feature_engineering import add_gold_features, add_event_features
# from src.database import create_tables, write_table
# from src.event_study import build_event_reactions
# from src.analytics import (
#     monthly_seasonality,
#     weekday_performance,
#     event_performance,
#     event_surprise_performance,
#     best_worst_event_reactions
# )
# from src.visualisations import create_all_charts
# from src.export_powerbi import export_all
# from src.config import DATA_PROCESSED_DIR
#
#
# def main():
#     print("Loading data...")
#     #raw_gold = load_from_yfinance("GC=F", start="2000-01-01")
#     raw_gold = load_gold_prices()
#     raw_events = load_economic_events()
#
#     print("Cleaning data...")
#     gold = clean_gold_prices(raw_gold)
#     events = clean_economic_events(raw_events)
#
#     print("Engineering features...")
#     gold = add_gold_features(gold)
#     events = add_event_features(events)
#
#     print("Running event study...")
#     reactions = build_event_reactions(gold, events)
#
#     print("Creating analytics summaries...")
#     monthly_summary = monthly_seasonality(gold)
#     weekday_summary = weekday_performance(gold)
#     event_summary = event_performance(reactions)
#     event_surprise_summary = event_surprise_performance(reactions)
#     best_worst_summary = best_worst_event_reactions(reactions)
#
#     print("Writing SQLite database...")
#     create_tables()
#     write_table(gold, "gold_prices")
#     write_table(events, "economic_events")
#     write_table(reactions, "gold_event_reactions")
#
#     print("Saving processed data...")
#     DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
#     gold.to_csv(DATA_PROCESSED_DIR / "gold_prices_processed.csv", index=False)
#     events.to_csv(DATA_PROCESSED_DIR / "economic_events_processed.csv", index=False)
#     reactions.to_csv(DATA_PROCESSED_DIR / "gold_event_reactions_processed.csv", index=False)
#
#     print("Exporting Power BI CSV files...")
#     export_paths = export_all(
#         gold,
#         events,
#         reactions,
#         monthly_summary,
#         weekday_summary,
#         event_summary,
#         event_surprise_summary,
#         best_worst_summary
#     )
#
#     print("Creating charts...")
#     chart_paths = create_all_charts(
#         gold,
#         monthly_summary,
#         weekday_summary,
#         event_summary,
#         reactions
#     )
#
#     print("\nDone.")
#     print(f"Power BI exports created: {len(export_paths)}")
#     print(f"Charts created: {len(chart_paths)}")
#     print("Open outputs/powerbi_exports/ and outputs/charts/ to review results.")
#
#
# if __name__ == "__main__":
#     main()

from src.data_loader import load_gold_prices, load_economic_events, load_from_yfinance
from src.data_cleaner import clean_gold_prices, clean_economic_events
from src.feature_engineering import add_gold_features, add_event_features
from src.database import create_tables, write_table
from src.event_study import build_event_reactions
from src.analytics import (
    monthly_seasonality,
    weekday_performance,
    event_performance,
    event_surprise_performance,
    best_worst_event_reactions,
)
from src.visualisations import create_all_charts
from src.export_powerbi import export_all
from src.config import DATA_RAW_DIR, DATA_PROCESSED_DIR


USE_YFINANCE_GOLD = False
YFINANCE_GOLD_TICKER = "GC=F"
START_DATE = "2000-01-01"


def main():
    print("Loading data...")

    if USE_YFINANCE_GOLD:
        print(f"Downloading real gold data from yfinance: {YFINANCE_GOLD_TICKER}")
        raw_gold = load_from_yfinance(YFINANCE_GOLD_TICKER, start=START_DATE)

        DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
        raw_gold.to_csv(DATA_RAW_DIR / "gold_prices.csv", index=False)

        print("Saved yfinance gold data to data/raw/gold_prices.csv")
    else:
        raw_gold = load_gold_prices()

    raw_events = load_economic_events()

    print("Cleaning data...")
    gold = clean_gold_prices(raw_gold)
    events = clean_economic_events(raw_events)

    print("Engineering features...")
    gold = add_gold_features(gold)
    events = add_event_features(events)

    print("Running event study...")
    reactions = build_event_reactions(gold, events)

    print("Gold rows:", len(gold))
    print("Event rows:", len(events))
    print("Reaction rows:", len(reactions))

    if not gold.empty:
        print("Gold date range:", gold["date"].min(), "to", gold["date"].max())

    if not events.empty:
        print("Event date range:", events["event_date"].min(), "to", events["event_date"].max())

    if reactions.empty:
        print("WARNING: No event reactions were created.")
        print("Check whether event dates overlap with gold price dates.")

    print("Creating analytics summaries...")
    monthly_summary = monthly_seasonality(gold)
    weekday_summary = weekday_performance(gold)
    event_summary = event_performance(reactions)
    event_surprise_summary = event_surprise_performance(reactions)
    best_worst_summary = best_worst_event_reactions(reactions)

    print("Writing SQLite database...")
    create_tables()
    write_table(gold, "gold_prices")
    write_table(events, "economic_events")
    write_table(reactions, "gold_event_reactions")

    print("Saving processed data...")
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    gold.to_csv(DATA_PROCESSED_DIR / "gold_prices_processed.csv", index=False)
    events.to_csv(DATA_PROCESSED_DIR / "economic_events_processed.csv", index=False)
    reactions.to_csv(DATA_PROCESSED_DIR / "gold_event_reactions_processed.csv", index=False)

    print("Exporting Power BI CSV files...")
    export_paths = export_all(
        gold,
        events,
        reactions,
        monthly_summary,
        weekday_summary,
        event_summary,
        event_surprise_summary,
        best_worst_summary,
    )

    print("Creating charts...")
    chart_paths = create_all_charts(
        gold,
        monthly_summary,
        weekday_summary,
        event_summary,
        reactions,
    )

    print("\nDone.")
    print(f"Power BI exports created: {len(export_paths)}")
    print(f"Charts created: {len(chart_paths)}")
    print("Open outputs/powerbi_exports/ and outputs/charts/ to review results.")


if __name__ == "__main__":
    main()