import pandas as pd
from pathlib import Path

from src.config import DATA_RAW_DIR, FRED_API_KEY
from src.data_loader import load_from_yfinance
from src.fred_loader import load_fred_series
from src.free_event_builder import build_events_from_fred_series


def download_market_data(start_date="2000-01-01"):
    """
    Download gold and macro market data from yfinance.
    """

    tickers = {
        "gold_prices.csv": "GC=F",
        "gld.csv": "GLD",
        "dxy.csv": "DX-Y.NYB",
        "us10y_yfinance.csv": "^TNX",
        "vix.csv": "^VIX",
        "sp500.csv": "^GSPC",
    }

    for filename, ticker in tickers.items():
        try:
            df = load_from_yfinance(ticker, start=start_date)
            output_path = DATA_RAW_DIR / filename
            df.to_csv(output_path, index=False)
            print(f"Saved {ticker} to {output_path}")
        except Exception as e:
            print(f"Failed to download {ticker}: {e}")


def download_fred_macro_data(start_date="2000-01-01"):
    """
    Download free macro data from FRED and create a macro_data.csv file.
    """

    if not FRED_API_KEY:
        raise ValueError("Missing FRED_API_KEY in .env file.")

    fred_series = {
        "cpi": "CPIAUCSL",
        "core_cpi": "CPILFESL",
        "unemployment": "UNRATE",
        "fed_funds": "FEDFUNDS",
        "pce": "PCEPI",
        "gdp": "GDP",
        "treasury_10y": "DGS10",
        "real_yield_10y": "DFII10",
    }

    all_series = []

    for name, series_id in fred_series.items():
        try:
            df = load_fred_series(series_id, FRED_API_KEY, start_date)
            df = df.rename(columns={series_id.lower(): name})
            all_series.append(df)
            print(f"Downloaded FRED series: {series_id}")
        except Exception as e:
            print(f"Failed to download FRED series {series_id}: {e}")

    if not all_series:
        raise ValueError("No FRED macro data downloaded.")

    macro = all_series[0]

    for df in all_series[1:]:
        macro = macro.merge(df, on="date", how="outer")

    macro = macro.sort_values("date")
    macro.to_csv(DATA_RAW_DIR / "macro_data.csv", index=False)

    return macro


def build_free_economic_events(start_date="2000-01-01"):
    """
    Build economic_events.csv using free FRED data.
    Forecast is unavailable, so surprise is actual minus previous.
    """

    if not FRED_API_KEY:
        raise ValueError("Missing FRED_API_KEY in .env file.")

    event_specs = [
        {
            "series_id": "CPIAUCSL",
            "value_column": "cpiaucsl",
            "event_name": "US CPI",
            "category": "Inflation",
            "impact": "High",
        },
        {
            "series_id": "CPILFESL",
            "value_column": "cpilfesl",
            "event_name": "US Core CPI",
            "category": "Inflation",
            "impact": "High",
        },
        {
            "series_id": "UNRATE",
            "value_column": "unrate",
            "event_name": "US Unemployment Rate",
            "category": "Labour Market",
            "impact": "High",
        },
        {
            "series_id": "FEDFUNDS",
            "value_column": "fedfunds",
            "event_name": "Fed Funds Rate",
            "category": "Monetary Policy",
            "impact": "High",
        },
        {
            "series_id": "PCEPI",
            "value_column": "pcepi",
            "event_name": "US PCE Price Index",
            "category": "Inflation",
            "impact": "High",
        },
        {
            "series_id": "GDP",
            "value_column": "gdp",
            "event_name": "US GDP",
            "category": "Growth",
            "impact": "High",
        },
    ]

    all_events = []

    for spec in event_specs:
        try:
            df = load_fred_series(spec["series_id"], FRED_API_KEY, start_date)

            events = build_events_from_fred_series(
                df=df,
                value_column=spec["value_column"],
                event_name=spec["event_name"],
                category=spec["category"],
                impact=spec["impact"],
            )

            all_events.append(events)
            print(f"Built events for {spec['event_name']}")

        except Exception as e:
            print(f"Failed to build events for {spec['event_name']}: {e}")

    if not all_events:
        raise ValueError("No economic events created.")

    economic_events = pd.concat(all_events, ignore_index=True)
    economic_events = economic_events.sort_values("event_date")

    output_path = DATA_RAW_DIR / "economic_events.csv"
    economic_events.to_csv(output_path, index=False)

    print(f"Saved free economic events to {output_path}")

    return economic_events


if __name__ == "__main__":
    download_market_data()
    download_fred_macro_data()
    build_free_economic_events()