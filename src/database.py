import sqlite3
import pandas as pd
from pathlib import Path
from .config import DATABASE_PATH


def get_connection(db_path: Path = DATABASE_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def create_tables(db_path: Path = DATABASE_PATH):
    with get_connection(db_path) as conn:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS gold_prices (
            date TEXT PRIMARY KEY,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            return_1d REAL,
            return_next_1d REAL,
            return_next_3d REAL,
            return_next_5d REAL,
            return_next_10d REAL,
            return_next_20d REAL,
            high_low_range_pct REAL,
            weekday TEXT,
            month TEXT,
            month_num INTEGER,
            year INTEGER,
            quarter INTEGER,
            rolling_20d_volatility REAL,
            ma_50 REAL,
            ma_200 REAL,
            trend_regime TEXT,
            volatility_regime TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS economic_events (
            event_id INTEGER PRIMARY KEY,
            event_date TEXT,
            event_time TEXT,
            country TEXT,
            event_name TEXT,
            category TEXT,
            actual TEXT,
            forecast TEXT,
            previous TEXT,
            actual_num REAL,
            forecast_num REAL,
            previous_num REAL,
            surprise REAL,
            surprise_direction TEXT,
            event_result TEXT,
            impact TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS gold_event_reactions (
            reaction_id INTEGER PRIMARY KEY,
            event_id INTEGER,
            event_date TEXT,
            matched_gold_date TEXT,
            event_name TEXT,
            category TEXT,
            surprise_direction TEXT,
            event_result TEXT,
            gold_close_before REAL,
            gold_close_event_day REAL,
            gold_close_after_1d REAL,
            gold_close_after_3d REAL,
            gold_close_after_5d REAL,
            gold_close_after_10d REAL,
            gold_close_after_20d REAL,
            return_0d REAL,
            return_1d REAL,
            return_3d REAL,
            return_5d REAL,
            return_10d REAL,
            return_20d REAL,
            max_gain_10d REAL,
            max_drawdown_10d REAL,
            direction_1d TEXT,
            direction_5d TEXT,
            direction_10d TEXT,
            FOREIGN KEY(event_id) REFERENCES economic_events(event_id)
        )
        """)

        conn.commit()


def write_table(df: pd.DataFrame, table_name: str, db_path: Path = DATABASE_PATH):
    """
    Safely write a DataFrame to SQLite.
    """

    if df is None:
        raise ValueError(f"{table_name} is None. Cannot write to database.")

    if len(df.columns) == 0:
        raise ValueError(
            f"{table_name} has zero columns. This means an earlier step failed."
        )

    with get_connection(db_path) as conn:
        out = df.copy()

        for col in out.columns:
            if pd.api.types.is_datetime64_any_dtype(out[col]):
                out[col] = out[col].dt.strftime("%Y-%m-%d")

        out.to_sql(table_name, conn, if_exists="replace", index=False)


def read_table(table_name: str, db_path: Path = DATABASE_PATH) -> pd.DataFrame:
    with get_connection(db_path) as conn:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
