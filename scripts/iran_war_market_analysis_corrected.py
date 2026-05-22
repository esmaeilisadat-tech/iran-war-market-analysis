#!/usr/bin/env python
# coding: utf-8

# # Iran War Market Analysis
# 
# **Project:** Impact of Iran war-related events on Oil, Gold, and EUR/USD  
# **Goal:** Load real CSV data, clean/merge it, calculate returns, use `groupby`, build MA/EMA indicators, visualize results, and write conclusions.
# 
# This notebook is adjusted for this project folder structure:
# 
# - iran-war-market-analysis/
# - iran-war-market-analysis/data/processed/
# - iran-war-market-analysis/notebooks/iran_war_market_analysis_corrected.ipynb
# - iran-war-market-analysis/outputs/figures/
# 

# ## 1. Import Libraries

# In[ ]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)


# ## 2. Define Project Paths
# 
# The notebook should be inside the `notebooks/` folder. The code below still works if you run it from the project root.

# In[ ]:


CURRENT_DIR = Path.cwd()
PROJECT_ROOT = CURRENT_DIR.parent if CURRENT_DIR.name.lower() == 'notebooks' else CURRENT_DIR

DATA_PATH = PROJECT_ROOT / 'data' / 'processed'
FIGURE_PATH = PROJECT_ROOT / 'outputs' / 'figures'

FIGURE_PATH.mkdir(parents=True, exist_ok=True)
DATA_PATH.mkdir(parents=True, exist_ok=True)

print('Project root:', PROJECT_ROOT)
print('Data path:', DATA_PATH)
print('Figure path:', FIGURE_PATH)


# ## 3. Load CSV Files

# In[ ]:


eurusd = pd.read_csv(DATA_PATH / 'eurusd_clean.csv')
gold = pd.read_csv(DATA_PATH / 'gold_clean.csv')
oil = pd.read_csv(DATA_PATH / 'oil_clean.csv')
war = pd.read_csv(DATA_PATH / 'war_master_dataset.csv')

print('EUR/USD shape:', eurusd.shape)
print('Gold shape:', gold.shape)
print('Oil shape:', oil.shape)
print('War events shape:', war.shape)


# In[ ]:


display(eurusd.head())
display(gold.head())
display(oil.head())
display(war.head())


# ## 4. Basic Data Cleaning
# 
# Steps:
# - Standardize date columns
# - Rename close price columns
# - Convert dates to datetime
# - Remove duplicate dates
# - Sort by date
# - Clean war event description column

# In[ ]:


def prepare_market_data(df, close_name):
    df = df.copy()
    df = df.rename(columns={'Date': 'date', 'Close': close_name})
    df['date'] = pd.to_datetime(df['date'])
    df = df[['date', close_name]].dropna()
    df = df.drop_duplicates(subset='date')
    df = df.sort_values('date').reset_index(drop=True)
    return df

eurusd = prepare_market_data(eurusd, 'eurusd_close')
gold = prepare_market_data(gold, 'gold_close')
oil = prepare_market_data(oil, 'oil_close')

war = war.copy()
war['date'] = pd.to_datetime(war['date'])

# Clean strange column name if it exists: description;;
war.columns = [c.replace(';', '').strip() for c in war.columns]
if 'description' not in war.columns:
    possible_description_cols = [c for c in war.columns if 'description' in c.lower()]
    if possible_description_cols:
        war = war.rename(columns={possible_description_cols[0]: 'description'})

war['description'] = war.get('description', 'Iran war-related event').astype(str).str.replace(';', '', regex=False).str.strip()
war = war.dropna(subset=['date']).drop_duplicates(subset=['date', 'description']).sort_values('date').reset_index(drop=True)

display(eurusd.head())
display(gold.head())
display(oil.head())
display(war.head())


# ## 5. Check Missing Values

# In[ ]:


print('EUR/USD missing values:')
print(eurusd.isnull().sum())

print('\nGold missing values:')
print(gold.isnull().sum())

print('\nOil missing values:')
print(oil.isnull().sum())

print('\nWar missing values:')
print(war.isnull().sum())


# ## 6. Merge Market Datasets
# 
# We merge Oil, Gold, and EUR/USD by date.

# In[ ]:


market = eurusd.merge(gold, on='date', how='inner').merge(oil, on='date', how='inner')
market = market.sort_values('date').reset_index(drop=True)

print('Merged market shape:', market.shape)
display(market.head())
display(market.tail())


# ## 7. Calculate Daily Returns
# 
# Daily return means the percentage change from the previous trading day.

# In[ ]:


market['eurusd_return'] = market['eurusd_close'].pct_change() * 100
market['gold_return'] = market['gold_close'].pct_change() * 100
market['oil_return'] = market['oil_close'].pct_change() * 100

market = market.dropna().reset_index(drop=True)
display(market.head())


# ## 8. Merge War Events With Market Data
# 
# Some war event dates may fall on weekends or market holidays. To avoid losing them, every event is mapped to the nearest next available trading date.

# In[ ]:


# Prepare market dates
market_dates = market[['date']].sort_values('date').copy()
war_sorted = war.sort_values('date').copy()

# Map every event date to the next available market date
war_mapped = pd.merge_asof(
    war_sorted,
    market_dates.rename(columns={'date': 'market_date'}),
    left_on='date',
    right_on='market_date',
    direction='forward'
)

war_mapped = war_mapped.dropna(subset=['market_date']).copy()
war_mapped['original_event_date'] = war_mapped['date']
war_mapped['date'] = war_mapped['market_date']

# Aggregate events that map to the same trading date
war_daily = (
    war_mapped
    .groupby('date', as_index=False)
    .agg(
        war_event=('description', 'count'),
        event_descriptions=('description', lambda x: ' | '.join(x)),
        categories=('category', lambda x: ' | '.join(sorted(set(map(str, x))))),
        max_severity=('severity', lambda x: ' | '.join(map(str, x)))
    )
)

merged = market.merge(war_daily, on='date', how='left')
merged['war_event'] = merged['war_event'].fillna(0).astype(int)
merged['has_war_event'] = np.where(merged['war_event'] > 0, 1, 0)
merged['event_descriptions'] = merged['event_descriptions'].fillna('No major Iran war-related event')
merged['categories'] = merged['categories'].fillna('No Event')

print('Final merged shape:', merged.shape)
display(merged.head())
display(merged[merged['has_war_event'] == 1].head())


# ## 9. Important Groupby Analysis
# 
# This section is important because `groupby` is one of the most useful tools in Data Science.

# In[ ]:


normal_vs_war_groupby = merged.groupby('has_war_event')[['eurusd_return', 'gold_return', 'oil_return']].mean()
normal_vs_war_groupby.index = normal_vs_war_groupby.index.map({0: 'Normal days', 1: 'War-event days'})

display(normal_vs_war_groupby)


# In[ ]:


# Monthly groupby analysis
merged['year_month'] = merged['date'].dt.to_period('M').astype(str)
monthly_groupby = merged.groupby('year_month')[['eurusd_return', 'gold_return', 'oil_return']].mean().reset_index()

display(monthly_groupby.head())


# In[ ]:


# Category groupby analysis
war_category_groupby = (
    merged[merged['has_war_event'] == 1]
    .groupby('categories')[['eurusd_return', 'gold_return', 'oil_return']]
    .mean()
    .reset_index()
)

display(war_category_groupby)


# ## 10. Event Window Analysis
# 
# For every war event, compare average returns 5 trading days before and 5 trading days after the event.

# In[ ]:


def analyze_event_window(market_df, event_df, window=5):
    results = []
    market_df = market_df.sort_values('date').reset_index(drop=True)

    for _, event in event_df.iterrows():
        event_date = event['date']
        idx_list = market_df.index[market_df['date'] == event_date].tolist()

        if not idx_list:
            continue

        idx = idx_list[0]
        before = market_df.iloc[max(0, idx-window):idx]
        after = market_df.iloc[idx+1:idx+1+window]

        results.append({
            'event_date': event_date,
            'event_descriptions': event.get('event_descriptions', ''),
            'eurusd_before_5d_avg_return': before['eurusd_return'].mean(),
            'eurusd_after_5d_avg_return': after['eurusd_return'].mean(),
            'gold_before_5d_avg_return': before['gold_return'].mean(),
            'gold_after_5d_avg_return': after['gold_return'].mean(),
            'oil_before_5d_avg_return': before['oil_return'].mean(),
            'oil_after_5d_avg_return': after['oil_return'].mean(),
        })

    result_df = pd.DataFrame(results)

    if not result_df.empty:
        result_df['eurusd_5d_change_after_event'] = result_df['eurusd_after_5d_avg_return'] - result_df['eurusd_before_5d_avg_return']
        result_df['gold_5d_change_after_event'] = result_df['gold_after_5d_avg_return'] - result_df['gold_before_5d_avg_return']
        result_df['oil_5d_change_after_event'] = result_df['oil_after_5d_avg_return'] - result_df['oil_before_5d_avg_return']

    return result_df

event_window_analysis = analyze_event_window(merged, war_daily, window=5)
display(event_window_analysis.head())


# ## 11. Add Moving Average and EMA Indicators
# 
# We create MA and EMA with different windows: 10, 20, and 50.
# 
# - MA = Moving Average, smoother but slower
# - EMA = Exponential Moving Average, reacts faster to recent changes

# In[ ]:


def add_ma_ema(df, price_col, base_name, windows=(10, 20, 50)):
    df = df.copy()
    for window in windows:
        df[f'{base_name}_ma_{window}'] = df[price_col].rolling(window=window).mean()
        df[f'{base_name}_ema_{window}'] = df[price_col].ewm(span=window, adjust=False).mean()
    return df

merged = add_ma_ema(merged, 'eurusd_close', 'eurusd')
merged = add_ma_ema(merged, 'gold_close', 'gold')
merged = add_ma_ema(merged, 'oil_close', 'oil')

display(merged.head())


# ## 12. Create Bullish / Bearish Indicator Signals
# 
# Simple rule:
# 
# - MA10 > MA50 means Bullish
# - MA10 <= MA50 means Bearish
# 
# Same idea for EMA.

# In[ ]:


for asset in ['eurusd', 'gold', 'oil']:
    merged[f'{asset}_ma_signal'] = np.where(
        merged[f'{asset}_ma_10'] > merged[f'{asset}_ma_50'],
        'Bullish',
        'Bearish'
    )

    merged[f'{asset}_ema_signal'] = np.where(
        merged[f'{asset}_ema_10'] > merged[f'{asset}_ema_50'],
        'Bullish',
        'Bearish'
    )

display(merged[[
    'date',
    'oil_close', 'oil_ma_10', 'oil_ma_50', 'oil_ma_signal', 'oil_ema_10', 'oil_ema_50', 'oil_ema_signal'
]].tail())


# ## 13. Groupby Performance of Indicator Signals
# 
# Here we use `groupby` again to compare average returns in Bullish and Bearish indicator conditions.

# In[ ]:


indicator_results = []

for asset in ['eurusd', 'gold', 'oil']:
    return_col = f'{asset}_return'

    for indicator_type in ['ma', 'ema']:
        signal_col = f'{asset}_{indicator_type}_signal'
        temp = (
            merged
            .dropna(subset=[return_col, signal_col])
            .groupby(signal_col)[return_col]
            .mean()
            .reset_index()
        )

        for _, row in temp.iterrows():
            indicator_results.append({
                'market': asset.upper(),
                'indicator': indicator_type.upper(),
                'signal': row[signal_col],
                'average_return': row[return_col]
            })

indicator_groupby_performance = pd.DataFrame(indicator_results)
display(indicator_groupby_performance)


# ## 14. Visualizations: War Events on Market Prices

# In[ ]:


def plot_price_with_events(df, price_col, title, ylabel, filename):
    plt.figure(figsize=(14, 6))
    plt.plot(df['date'], df[price_col], label=ylabel)

    for event_date in df.loc[df['has_war_event'] == 1, 'date']:
        plt.axvline(event_date, linestyle='--', alpha=0.35)

    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURE_PATH / filename, dpi=300, bbox_inches='tight')
    plt.show()

plot_price_with_events(merged, 'oil_close', 'Oil Price with Iran War-Related Events', 'Oil Price', 'oil_war_events.png')
plot_price_with_events(merged, 'gold_close', 'Gold Price with Iran War-Related Events', 'Gold Price', 'gold_war_events.png')
plot_price_with_events(merged, 'eurusd_close', 'EUR/USD with Iran War-Related Events', 'EUR/USD', 'eurusd_war_events.png')


# ## 15. Visualizations: MA and EMA Indicators

# In[ ]:


def plot_ma_ema(df, asset, price_col, title, ylabel, filename):
    plt.figure(figsize=(14, 6))
    plt.plot(df['date'], df[price_col], label='Close')
    plt.plot(df['date'], df[f'{asset}_ma_20'], label='MA 20')
    plt.plot(df['date'], df[f'{asset}_ema_20'], label='EMA 20')
    plt.plot(df['date'], df[f'{asset}_ma_50'], label='MA 50')

    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURE_PATH / filename, dpi=300, bbox_inches='tight')
    plt.show()

plot_ma_ema(merged, 'oil', 'oil_close', 'Oil Price with MA and EMA Indicators', 'Oil Price', 'oil_ma_ema_indicator_chart.png')
plot_ma_ema(merged, 'gold', 'gold_close', 'Gold Price with MA and EMA Indicators', 'Gold Price', 'gold_ma_ema_indicator_chart.png')
plot_ma_ema(merged, 'eurusd', 'eurusd_close', 'EUR/USD with MA and EMA Indicators', 'EUR/USD', 'eurusd_ma_ema_indicator_chart.png')


# ## 16. Visualizations: Average 5-Day Change After Events

# In[ ]:


avg_5d_change = pd.DataFrame({
    'market': ['EUR/USD', 'Gold', 'Oil'],
    'average_5d_change_after_event': [
        event_window_analysis['eurusd_5d_change_after_event'].mean(),
        event_window_analysis['gold_5d_change_after_event'].mean(),
        event_window_analysis['oil_5d_change_after_event'].mean(),
    ]
})

display(avg_5d_change)

plt.figure(figsize=(8, 5))
sns.barplot(data=avg_5d_change, x='market', y='average_5d_change_after_event')
plt.title('Average 5-Day Return Change After Iran War-Related Events')
plt.xlabel('Market')
plt.ylabel('Average Change in Return (%)')
plt.grid(True, axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURE_PATH / 'avg_5d_change_after_events.png', dpi=300, bbox_inches='tight')
plt.show()


# ## 17. Visualizations: EMA Signal Groupby Performance

# In[ ]:


ema_perf = indicator_groupby_performance[indicator_groupby_performance['indicator'] == 'EMA']

plt.figure(figsize=(9, 5))
sns.barplot(data=ema_perf, x='market', y='average_return', hue='signal')
plt.title('Average Return by EMA Signal')
plt.xlabel('Market')
plt.ylabel('Average Daily Return (%)')
plt.grid(True, axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURE_PATH / 'ema_signal_groupby_performance.png', dpi=300, bbox_inches='tight')
plt.show()


# ## 18. Save Final CSV Outputs

# In[ ]:


merged.to_csv(DATA_PATH / 'merged_market_war_with_indicators.csv', index=False)
normal_vs_war_groupby.to_csv(DATA_PATH / 'normal_vs_war_groupby_summary.csv')
monthly_groupby.to_csv(DATA_PATH / 'monthly_groupby_return_summary.csv', index=False)
war_category_groupby.to_csv(DATA_PATH / 'war_category_groupby_summary.csv', index=False)
indicator_groupby_performance.to_csv(DATA_PATH / 'indicator_groupby_performance.csv', index=False)
event_window_analysis.to_csv(DATA_PATH / 'event_window_analysis.csv', index=False)

print('Saved CSV outputs to:', DATA_PATH)
print('Saved figures to:', FIGURE_PATH)


# ## 19. Final Conclusion
# 
# This project used real market data for oil, gold, and EUR/USD. The data was loaded from CSV files, cleaned, merged by date, and analyzed using daily returns.
# 
# Important points demonstrated in this project:
# 
# - CSV data loading with Pandas
# - Basic data cleaning
# - Merging multiple datasets by date
# - Daily return calculation
# - `groupby` analysis for normal days vs war-event days
# - MA and EMA indicator calculation
# - Bullish/Bearish signal comparison
# - Visualization with Matplotlib and Seaborn
# 
# **Main interpretation:**
# 
# Oil, gold, and EUR/USD show different behavior around Iran war-related events. This analysis does not prove causation, but it shows visible market behavior around geopolitical events.
# 
# **Limitations:**
# 
# - A small number of war events
# - Other market factors may affect prices
# - Correlation does not prove causation
# - More advanced statistical tests could improve the analysis
# 
