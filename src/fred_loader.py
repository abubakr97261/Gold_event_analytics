import requests
import pandas as pd


def load_fred_series(series_id, api_key, start_date="2000-01-01"):
    """
    Load actual historical macroeconomic data from FRED.

    Example series:
    CPIAUCSL = CPI
    CPILFESL = Core CPI
    UNRATE = Unemployment rate
    FEDFUNDS = Fed funds rate
    GDP = Gross domestic product
    PCEPI = PCE price index
    DGS10 = 10-year Treasury yield
    DFII10 = 10-year real yield
    """

    url = "https://api.stlouisfed.org/fred/series/observations"

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json().get("observations", [])

    if not data:
        raise ValueError(f"No data returned from FRED for {series_id}")

    df = pd.DataFrame(data)

    df = df[["date", "value"]]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df.rename(columns={"value": series_id.lower()})