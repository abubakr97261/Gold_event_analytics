import requests
import pandas as pd


def load_fred_release_dates(release_id, api_key, start_date="2000-01-01", end_date=None):
    """
    Load release dates for a FRED release.

    Common FRED release IDs:
    10 = Consumer Price Index
    50 = Employment Situation
    53 = Gross Domestic Product
    54 = Personal Income and Outlays
    18 = H.15 Selected Interest Rates

    Note:
    FRED release IDs should be verified from FRED release metadata.
    """

    url = "https://api.stlouisfed.org/fred/release/dates"

    params = {
        "release_id": release_id,
        "api_key": api_key,
        "file_type": "json",
        "realtime_start": start_date,
    }

    if end_date:
        params["realtime_end"] = end_date

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json().get("release_dates", [])

    if not data:
        raise ValueError(f"No release dates returned for release_id={release_id}")

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])

    return df