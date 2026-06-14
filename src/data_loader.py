import pandas as pd
from pathlib import Path
from .config import GOLD_CSV_PATH, EVENTS_CSV_PATH, OPTIONAL_YFINANCE_SYMBOL, YFINANCE_START_DATE, YFINANCE_END_DATE
import pandas as pd


def load_from_yfinance(ticker: str, start="2000-01-01", end=None):
    """
    Download daily OHLCV data from yfinance.

    Returns standard columns:
    date, open, high, low, close, volume
    """

    import pandas as pd

    try:
        import yfinance as yf
    except ImportError:
        raise ImportError("yfinance is not installed. Run: pip install yfinance")

    df = yf.download(
        ticker,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=False,
        progress=False,
        group_by="column"
    )

    if df.empty:
        raise ValueError(f"No data returned from yfinance for ticker: {ticker}")

    # If yfinance returns MultiIndex columns, flatten them
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    # Standardise column names
    df.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in df.columns
    ]

    # IMPORTANT FIX:
    # Some yfinance versions return the date column as "index"
    if "date" not in df.columns and "index" in df.columns:
        df = df.rename(columns={"index": "date"})

    if "datetime" in df.columns and "date" not in df.columns:
        df = df.rename(columns={"datetime": "date"})

    required_cols = ["date", "open", "high", "low", "close", "volume"]

    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required yfinance columns: {missing}. "
            f"Available columns: {list(df.columns)}"
        )

    df = df[required_cols].copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["date", "close"])
    df = df.sort_values("date")
    df = df.drop_duplicates(subset=["date"])

    return df

def load_gold_prices(csv_path: Path = GOLD_CSV_PATH, use_yfinance_if_missing: bool = True) -> pd.DataFrame:
    """Load gold price data from CSV. Optionally fetch with yfinance if CSV is missing."""
    if csv_path.exists():
        return pd.read_csv(csv_path)

    if use_yfinance_if_missing:
        try:
            import yfinance as yf
            data = yf.download(
                OPTIONAL_YFINANCE_SYMBOL,
                start=YFINANCE_START_DATE,
                end=YFINANCE_END_DATE,
                progress=False,
                auto_adjust=False
            )
            if data.empty:
                raise ValueError("yfinance returned no data.")

            data = data.reset_index()
            data = data.rename(columns={
                "Date": "Date",
                "Open": "Open",
                "High": "High",
                "Low": "Low",
                "Close": "Close",
                "Volume": "Volume"
            })
            required = ["Date", "Open", "High", "Low", "Close", "Volume"]
            return data[required]
        except Exception as exc:
            raise FileNotFoundError(
                f"Could not load {csv_path} and yfinance fallback failed: {exc}"
            ) from exc

    raise FileNotFoundError(f"Gold price CSV not found: {csv_path}")


def load_economic_events(csv_path: Path = EVENTS_CSV_PATH) -> pd.DataFrame:
    """Load economic event calendar data from CSV."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Economic events CSV not found: {csv_path}")
    return pd.read_csv(csv_path)
