# Iran War Market Analysis

## Project Overview

This project analyzes the possible impact of Iran war-related events on three financial markets:

- Oil
- Gold
- EUR/USD exchange rate

The goal is not to predict the market perfectly. The goal is to use a simple Data Science workflow to check whether geopolitical events are associated with visible changes in market behavior.

## Main Research Question

How do oil, gold, and EUR/USD behave around Iran war-related events?

More specifically, this project compares:

- Normal market days vs. war-event days
- Average returns before and after war-related events
- Market behavior using Moving Average and EMA indicators

## Project Structure

```text
iran-war-market-analysis/
│
├── data/
│   └── processed/
│       ├── eurusd_clean.csv
│       ├── gold_clean.csv
│       ├── oil_clean.csv
│       ├── war_master_dataset.csv
│       ├── merged_market_war_with_indicators.csv
│       ├── normal_vs_war_groupby_summary.csv
│       ├── war_category_groupby_summary.csv
│       ├── monthly_groupby_return_summary.csv
│       └── indicator_groupby_performance.csv
│
├── notebooks/
│   └── iran_war_market_analysis_corrected.ipynb
│
├── outputs/
│   └── figures/
│       ├── oil_war_events.png
│       ├── gold_war_events.png
│       ├── eurusd_war_events.png
│       ├── oil_ma_ema_indicator_chart.png
│       ├── gold_ma_ema_indicator_chart.png
│       ├── eurusd_ma_ema_indicator_chart.png
│       ├── ema_signal_groupby_performance.png
│       └── avg_5d_change_after_events.png
│
├── README.md
└── requirements.txt
```

## Data

The project uses cleaned CSV files stored in the `data/processed` folder:

- `eurusd_clean.csv`: EUR/USD exchange rate data
- `gold_clean.csv`: Gold price data
- `oil_clean.csv`: Oil price data
- `war_master_dataset.csv`: Iran war-related event dates and event information

The CSV files are already cleaned, so the project focuses on merging, analysis, indicators, visualization, and interpretation.

## Tools and Libraries

This project uses:

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Jupyter Notebook

Install the required libraries with:

```bash
pip install -r requirements.txt
```

## Methodology

The project follows a simple Data Science workflow:

1. Load CSV files with Pandas
2. Clean and standardize date columns
3. Merge oil, gold, EUR/USD, and war-event data by date
4. Calculate daily percentage returns
5. Use `groupby` to compare normal days and war-event days
6. Analyze average market behavior before and after war-related events
7. Create Moving Average and EMA indicators
8. Compare bullish and bearish indicator signals
9. Create visualizations
10. Write a conclusion based on the results

## Important Analysis Methods

### Daily Return

Daily return is calculated using percentage change:

```python
df["oil_return"] = df["oil_close"].pct_change() * 100
```

### Groupby Analysis

`groupby` is used to compare average market returns between normal days and war-event days:

```python
merged.groupby("war_event")[[
    "eurusd_return",
    "gold_return",
    "oil_return"
]].mean()
```

This is an important part of the project because it shows how data can be grouped and analyzed by category.

### Moving Average and EMA

The project also calculates technical indicators:

- MA 10, MA 20, MA 50
- EMA 10, EMA 20, EMA 50

Example:

```python
merged["oil_ma_20"] = merged["oil_close"].rolling(window=20).mean()
merged["oil_ema_20"] = merged["oil_close"].ewm(span=20, adjust=False).mean()
```

MA is smoother and slower. EMA reacts faster to recent market changes.

## Outputs

The notebook generates:

### Processed CSV outputs

Saved in `data/processed`:

- `merged_market_war_with_indicators.csv`
- `normal_vs_war_groupby_summary.csv`
- `war_category_groupby_summary.csv`
- `monthly_groupby_return_summary.csv`
- `indicator_groupby_performance.csv`

### Figures

Saved in `outputs/figures`:

- Oil price with war-event lines
- Gold price with war-event lines
- EUR/USD with war-event lines
- Oil MA/EMA indicator chart
- Gold MA/EMA indicator chart
- EUR/USD MA/EMA indicator chart
- EMA signal performance chart
- Average 5-day change after events chart

## How to Run the Project

1. Open the project folder:

```text
C:\git-projects\my-first-project\iran-war-market-analysis
```

2. Open the notebook:

```text
notebooks/iran_war_market_analysis_corrected.ipynb
```

3. Make sure the main path inside the notebook is correct:

```python
PROJECT_ROOT = Path(r"C:\git-projects\my-first-project\iran-war-market-analysis")
```

4. Run all cells from top to bottom.

The notebook will load the data, run the analysis, create summary CSV files, and save the charts.

## Main Conclusion

The analysis shows that oil, gold, and EUR/USD react differently around Iran war-related events.

In this dataset, oil shows the strongest positive average change after war-related events. Gold and EUR/USD show weaker or negative average reactions in some parts of the analysis.

The EMA indicator is useful because it reacts faster to recent market changes than the simple Moving Average.

## Limitations

This project has some limitations:

- The number of war-related events is limited.
- Other global factors may also affect oil, gold, and EUR/USD prices.
- Correlation does not prove causation.
- More advanced statistical methods could improve the analysis.

## Final Presentation Message

This project demonstrates a complete introductory Data Science workflow:

- Data loading
- Data cleaning
- Data merging
- Feature engineering
- Groupby analysis
- Indicator calculation
- Visualization
- Interpretation

The purpose is not perfect market prediction, but understanding visible market behavior around geopolitical events.
