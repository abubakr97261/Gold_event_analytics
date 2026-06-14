# Gold Historical Event Reaction Analytics System

This project analyses historical gold performance by month, weekday, and macroeconomic events such as CPI, NFP, FOMC, PCE, GDP, unemployment, retail sales, ISM PMI, and geopolitical/manual events.

## What it does

- Loads gold price data from `data/raw/gold_prices.csv`
- Optionally downloads gold data using `yfinance`
- Loads event data from `data/raw/economic_events.csv`
- Cleans and standardises both datasets
- Calculates gold forward returns for 1, 3, 5, 10, and 20 trading days
- Matches economic events to the next available gold trading day
- Calculates event-day and post-event gold reactions
- Stores cleaned data and reaction tables in SQLite
- Exports Power BI-ready CSV files
- Produces matplotlib charts

## Folder structure

```text
gold_event_analytics/
├── data/
│   ├── raw/
│   │   ├── gold_prices.csv
│   │   └── economic_events.csv
│   ├── processed/
├── outputs/
│   ├── charts/
│   └── powerbi_exports/
├── database/
│   └── gold_event_analytics.db
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── data_cleaner.py
│   ├── feature_engineering.py
│   ├── database.py
│   ├── event_study.py
│   ├── analytics.py
│   ├── visualisations.py
│   └── export_powerbi.py
├── main.py
├── requirements.txt
└── README.md
```

## How to run

1. Open a terminal in this folder.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the project:

```bash
python main.py
```

## Input CSV formats

### `data/raw/gold_prices.csv`

Required columns:

```text
Date,Open,High,Low,Close,Volume
```

### `data/raw/economic_events.csv`

Required columns:

```text
event_date,event_time,country,event_name,category,actual,forecast,previous,impact
```

`actual`, `forecast`, and `previous` can contain numbers or text. Numeric values are used for surprise calculations.

## Power BI outputs

After running `main.py`, import these files from `outputs/powerbi_exports/` into Power BI:

- `gold_prices_clean.csv`
- `economic_events_clean.csv`
- `gold_event_reactions.csv`
- `monthly_seasonality_summary.csv`
- `weekday_performance_summary.csv`
- `event_performance_summary.csv`
- `event_surprise_summary.csv`
- `best_worst_event_reactions.csv`

## Suggested Power BI pages

### Page 1: Gold Overview

Visuals:
- Current price card
- YTD return card
- Monthly return card
- 30-day volatility card
- Gold close price line chart
- Yearly return bar chart

### Page 2: Seasonality Analysis

Visuals:
- Average return by month
- Month win rate
- Weekday performance
- Year-month heatmap

### Page 3: Economic Event Reaction

Visuals:
- Event type slicer
- Year slicer
- Surprise direction slicer
- Event reaction table
- Average return by event type

### Page 4: Event Study

Visuals:
- Event selector
- Returns across 0D, 1D, 3D, 5D, 10D, 20D
- Max gain and drawdown table

### Page 5: Strategy Insights

Visuals:
- Strongest bullish events
- Strongest bearish events
- Best months
- Worst months
- Highest win-rate conditions
- Risk warning text box

## Suggested DAX measures

```DAX
Average Return 1D = AVERAGE(gold_event_reactions[return_1d])

Average Return 5D = AVERAGE(gold_event_reactions[return_5d])

Average Return 10D = AVERAGE(gold_event_reactions[return_10d])

Win Rate 1D =
DIVIDE(
    COUNTROWS(FILTER(gold_event_reactions, gold_event_reactions[return_1d] > 0)),
    COUNTROWS(gold_event_reactions)
)

Win Rate 5D =
DIVIDE(
    COUNTROWS(FILTER(gold_event_reactions, gold_event_reactions[return_5d] > 0)),
    COUNTROWS(gold_event_reactions)
)

Average Max Gain 10D = AVERAGE(gold_event_reactions[max_gain_10d])

Average Max Drawdown 10D = AVERAGE(gold_event_reactions[max_drawdown_10d])

Latest Gold Close =
CALCULATE(
    MAX(gold_prices[close]),
    FILTER(gold_prices, gold_prices[date] = MAX(gold_prices[date]))
)

YTD Return =
VAR StartPrice =
    CALCULATE(
        MIN(gold_prices[close]),
        DATESYTD(gold_prices[date])
    )
VAR EndPrice =
    CALCULATE(
        MAX(gold_prices[close]),
        DATESYTD(gold_prices[date])
    )
RETURN
DIVIDE(EndPrice - StartPrice, StartPrice)
```

## Limitations and warnings

- Event reaction analysis is historical, not predictive certainty.
- Correlation does not prove causation.
- Event time zones matter. A US release may occur before or after your chosen gold close.
- Same-day reaction can be misleading if using daily data only.
- Intraday gold data is better for CPI, NFP, and FOMC analysis.
- Forecast and actual values from economic calendars may be revised.
- Data licensing matters for professional/commercial use.
- Avoid look-ahead bias: only use information available at the event time.
- Weekend/holiday matching may shift events to the next trading day.
- Manual geopolitical event tagging can introduce selection bias.
