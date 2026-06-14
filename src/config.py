from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
CHARTS_DIR = OUTPUT_DIR / "charts"
POWERBI_EXPORT_DIR = OUTPUT_DIR / "powerbi_exports"
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "gold_event_analytics.db"

load_dotenv(BASE_DIR / "src" / ".env")

FRED_API_KEY = os.getenv("FRED_API_KEY")

GOLD_CSV_PATH = DATA_RAW_DIR / "gold_prices.csv"
EVENTS_CSV_PATH = DATA_RAW_DIR / "economic_events.csv"

for path in [
    DATA_RAW_DIR,
    DATA_PROCESSED_DIR,
    CHARTS_DIR,
    POWERBI_EXPORT_DIR,
    DATABASE_DIR,
]:
    path.mkdir(parents=True, exist_ok=True)

OPTIONAL_YFINANCE_SYMBOL = "GC=F"  # Gold futures. Alternatives: "GLD", "XAUUSD=X"
YFINANCE_START_DATE = "2000-01-01"
YFINANCE_END_DATE = None

FORWARD_WINDOWS = [1, 3, 5, 10, 20]
