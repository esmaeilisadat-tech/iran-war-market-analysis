#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[ ]:


from pathlib import Path

# نام پروژه
project_name = "iran-war-market-analysis"

# ساختار فولدرها
folders = [
    f"{project_name}",
    f"{project_name}/data/raw",
    f"{project_name}/data/external",
    f"{project_name}/data/processed",
    f"{project_name}/notebooks",
    f"{project_name}/src",
    f"{project_name}/visuals",
    f"{project_name}/reports",
]

# ساخت فولدرها
for folder in folders:
    Path(folder).mkdir(parents=True, exist_ok=True)
    print(f"Created: {folder}")

print("Project structure created successfully!")


# In[ ]:


pip install yfinance pandas numpy matplotlib


# In[ ]:


import yfinance as yf
import pandas as pd

oil = yf.download("BZ=F", start="2024-01-01", end="2026-05-20")


# In[ ]:


gold = yf.download("GC=F", start="2024-01-01", end="2026-05-20")


# In[ ]:


eurusd = yf.download("EURUSD=X", start="2024-01-01", end="2026-05-20")


# In[ ]:


import os

print(os.getcwd())
print(os.path.exists("data"))
print(os.path.exists("data/external"))
print(type(oil))
print(oil.shape)
print(oil.head())


# In[ ]:


import pandas as pd

def fix_yahoo(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    return df


# In[ ]:


oil = fix_yahoo(oil)
gold = fix_yahoo(gold)
eurusd = fix_yahoo(eurusd)


# In[ ]:


print(oil.columns)
print(gold.columns)
print(eurusd.columns)


# In[ ]:


import os

os.makedirs("data/external", exist_ok=True)

if 'oil' in globals() and oil is not None:
    oil.to_csv("data/external/oil.csv")
else:
    print("Warning: 'oil' is not defined — skipping save")

gold.to_csv("data/external/gold.csv")
eurusd.to_csv("data/external/eurusd.csv")
gold.to_csv("data/external/gold.csv")
eurusd.to_csv("data/external/eurusd.csv")


# In[ ]:


oil = oil[["Close"]]
gold = gold[["Close"]]
eurusd = eurusd[["Close"]]


# In[ ]:


oil_close = oil["Close"].rename("oil")
gold_close = gold["Close"].rename("gold")
eurusd_close = eurusd["Close"].rename("eurusd")


# In[ ]:


import pandas as pd

df = pd.concat([oil_close, gold_close, eurusd_close], axis=1)
df = df.dropna()
print(df.head())
print(df.info())


# In[ ]:


df_norm = df / df.iloc[0] * 100


# In[ ]:


import os

os.chdir(r"c:\git-projects\my-first-project\iran-war-market-analysis")
print(os.getcwd())


# In[ ]:


df.to_csv("data/processed/market_merged.csv")
df_norm.to_csv("data/processed/market_normalized.csv")


# In[ ]:


import os

BASE_DIR = r"c:\git-projects\my-first-project\iran-war-market-analysis"

processed_path = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(processed_path, exist_ok=True)

df.to_csv(os.path.join(processed_path, "market_merged.csv"))


# In[ ]:


import pandas as pd
import os

BASE = r"c:\git-projects\my-first-project\iran-war-market-analysis"

market = pd.read_csv(
    os.path.join(BASE, "data/processed/market_merged.csv"),
    index_col=0,
    parse_dates=True
)

timeline = pd.read_csv(
    os.path.join(BASE, "data/external/war/timeline.csv")
)

timeline["date"] = pd.to_datetime(timeline["date"])
timeline = timeline.sort_values("date")


# In[ ]:


market["war_event"] = 0


# In[ ]:


for d in timeline["date"]:
    if d in market.index:
        market.loc[d, "war_event"] = 1


# In[ ]:


master = market.copy()

master[["oil", "gold", "eurusd"]] = master[["oil", "gold", "eurusd"]].pct_change()

master = master.dropna()
print(master.head())
print(master.info())    



# In[ ]:


master.to_csv(os.path.join(BASE, "data/processed/master_dataset.csv"))


# In[ ]:


import os

os.chdir(r"C:\git-projects\my-first-project\iran-war-market-analysis")
print(os.getcwd())


# In[ ]:


import pandas as pd
import os

# =========================
# BASE PATH (FIXED)
# =========================
base_path = "data/external/war"

# =========================
# LOAD DATASETS
# =========================
timeline = pd.read_csv(f"{base_path}/timeline.csv")
economic = pd.read_csv(f"{base_path}/economic_impact.csv")
casualties = pd.read_csv(f"{base_path}/casualties.csv", usecols=["Date"])
infra = pd.read_csv(f"{base_path}/infrastructure_damage.csv")
aircraft = pd.read_csv(f"{base_path}/aircraft_losses.csv")
naval = pd.read_csv(f"{base_path}/naval_losses.csv")

# =========================
# DATE FIX
# =========================
for df in [timeline, economic, casualties, infra, aircraft, naval]:
    df["Date"] = pd.to_datetime(df["Date"])

# =========================
# MERGE MASTER DATASET
# =========================
df = timeline.copy()

df = df.merge(economic, on="Date", how="outer")
df = df.merge(casualties, on="Date", how="outer")
df = df.merge(infra, on="Date", how="outer")
df = df.merge(aircraft, on="Date", how="outer")
df = df.merge(naval, on="Date", how="outer")

df = df.sort_values("Date")

# =========================
# SAVE OUTPUT
# =========================
os.makedirs("data/processed", exist_ok=True)
df.to_csv("data/processed/master_dataset.csv", index=False)

print("DONE: Master dataset created")


# In[ ]:


import os

os.remove("data/external/war/casualties.csv")
print("deleted")


# In[ ]:


import yfinance as yf

oil = yf.download("BZ=F", start="2024-01-01")
gold = yf.download("GC=F", start="2024-01-01")
eurusd = yf.download("EURUSD=X", start="2024-01-01")


# In[ ]:


oil = oil.reset_index()
gold = gold.reset_index()
eurusd = eurusd.reset_index()
market = oil[["Date","Close"]].rename(columns={"Close":"Oil"})
market = market.merge(gold[["Date","Close"]].rename(columns={"Close":"Gold"}), on="Date", how="outer")
market = market.merge(eurusd[["Date","Close"]].rename(columns={"Close":"EURUSD"}), on="Date", how="outer")


# In[ ]:


import os
import pandas as pd

base_path = r"C:\git-projects\my-first-project\iran-war-market-analysis\data\external"

war_path = f"{base_path}\war"
market_path = f"{base_path}\market"
timeline = pd.read_csv(f"{war_path}/timeline.csv")
economic = pd.read_csv(f"{war_path}/economic_impact.csv")
infra = pd.read_csv(f"{war_path}/infrastructure_damage.csv")
aircraft = pd.read_csv(f"{war_path}/aircraft_losses.csv")
naval = pd.read_csv(f"{war_path}/naval_losses.csv") 


# In[ ]:


def inspect_csv(folder_path):
    files = os.listdir(folder_path)

    for file in files:
        if file.endswith(".csv"):
            path = os.path.join(folder_path, file)

            print("\n" + "="*50)
            print("FILE:", file)

            df = pd.read_csv(path)

            print("SHAPE:", df.shape)
            print("COLUMNS:", df.columns.tolist())
            print("HEAD:")
            print(df.head(6))
inspect_csv(war_path)   
inspect_csv(market_path)    



# In[ ]:


import pandas as pd

# =========================
# PATH
# =========================
base_path = r"C:\git-projects\my-first-project\iran-war-market-analysis\data\external\war"

# =========================
# LOAD DATA
# =========================
timeline = pd.read_csv(f"{base_path}/timeline.csv")
infra = pd.read_csv(f"{base_path}/infrastructure_damage.csv")

# =========================
# STANDARDIZE COLUMNS
# =========================
timeline.columns = timeline.columns.str.lower()
infra.columns = infra.columns.str.lower()

# =========================
# DATE PARSING
# =========================
timeline["date"] = pd.to_datetime(timeline["date"], errors="coerce")
infra["date"] = pd.to_datetime(infra["date"], errors="coerce")

# =========================
# CLEAN TIMELINE
# =========================
timeline_clean = (
    timeline[["date", "event", "category", "significance"]]
    .dropna(subset=["date"])
    .sort_values("date")
    .reset_index(drop=True)
)

# =========================
# CLEAN INFRASTRUCTURE
# =========================
infra_clean = (
    infra[['date', 'attacking_side', 'target_country', 'target_name', 'target_type', 'status', 'notes;;']]
    .rename(columns={'notes;;': 'notes'})
    .dropna(subset=["date"])
    .sort_values("date")
    .reset_index(drop=True)
)

# =========================
# OUTPUT CHECK
# =========================
print("TIMELINE CLEAN:")
print(timeline_clean.head())

print("\nINFRASTRUCTURE CLEAN:")
print(infra_clean.head())
output_path = r"C:\git-projects\my-first-project\iran-war-market-analysis\data\processed"

timeline_clean.to_csv(f"{output_path}/timeline_clean.csv", index=False)
infra_clean.to_csv(f"{output_path}/infra_clean.csv", index=False)

print("Files saved successfully!")


# In[ ]:


import pandas as pd

base_path = r"C:\git-projects\my-first-project\iran-war-market-analysis\data\external\war"
output_path = r"C:\git-projects\my-first-project\iran-war-market-analysis\data\processed"

# =========================
# LOAD
# =========================
timeline = pd.read_csv(f"{base_path}/timeline.csv")
infra = pd.read_csv(f"{base_path}/infrastructure_damage.csv")

# =========================
# LOWERCASE COLUMNS
# =========================
timeline.columns = timeline.columns.str.lower()
infra.columns = infra.columns.str.lower()

# =========================
# STANDARD DATE
# =========================
timeline["date"] = pd.to_datetime(timeline["date"], errors="coerce")
infra["date"] = pd.to_datetime(infra["date"], errors="coerce")

# =========================
# NORMALIZE TIMELINE
# =========================
timeline_clean = timeline.rename(columns={
    "event": "description"
})

timeline_clean["type"] = "timeline"

timeline_clean = timeline_clean[[
    "date", "type", "category", "significance", "description"
]]

timeline_clean = timeline_clean.rename(columns={
    "significance": "severity"
})

# =========================
# NORMALIZE INFRASTRUCTURE
# =========================
infra_clean = infra.rename(columns={
    "damage_type": "category",
    "notes": "description"
})

infra_clean["type"] = "infrastructure"

infra_clean = infra.rename(columns={
    "target_type": "category",
    "notes;;": "description"
})
infra_clean["type"] = "infrastructure"
infra_clean["severity"] = infra_clean["status"]
infra_clean = infra_clean[[
    "date", "type", "category", "severity", "description"
]]

# =========================
# ALIGN SCHEMAS
# =========================
common_cols = ["date", "type", "category", "severity", "description"]

timeline_clean = timeline_clean[common_cols]
infra_clean = infra_clean[common_cols]

# =========================
# UNION (STACK ROWS)
# =========================
war_master = pd.concat([timeline_clean, infra_clean], ignore_index=True)

# =========================
# SORT
# =========================
war_master = war_master.sort_values("date").reset_index(drop=True)

# =========================
# SAVE
# =========================
war_master.to_csv(f"{output_path}/war_master_dataset.csv", index=False)

print(war_master.head())
print("\nSaved successfully!")


# In[ ]:


import pandas as pd
import os

# =========================
# 1. BASE PATH
# =========================
base_path = r"C:\git-projects\my-first-project\iran-war-market-analysis"

raw_path = os.path.join(base_path, "data", "external", "market")
out_path = os.path.join(base_path, "data", "processed")

os.makedirs(out_path, exist_ok=True)

# =========================
# 2. LOAD DATA
# =========================
oil = pd.read_csv(os.path.join(raw_path, "oil.csv"))
gold = pd.read_csv(os.path.join(raw_path, "gold.csv"))
eurusd = pd.read_csv(os.path.join(raw_path, "eurusd.csv"))

# =========================
# 3. STANDARDIZE FUNCTION
# =========================
def clean_market(df):
    # اگر ستون‌ها MultiIndex باشن (مثل Yahoo)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.rename(columns={
        "Adj Close": "Close"
    })

    # فقط ستون‌های اصلی
    df = df[["Date", "Close", "High", "Low", "Open", "Volume"]]

    # تاریخ
    df["Date"] = pd.to_datetime(df["Date"])

    # فیلتر زمانی
    df = df[df["Date"] >= "2025-04-01"]

    return df.sort_values("Date")


# =========================
# 4. CLEAN ALL MARKETS
# =========================
oil = clean_market(oil)
gold = clean_market(gold)
eurusd = clean_market(eurusd)

# =========================
# 5. SAVE CLEAN DATA
# =========================
oil.to_csv(os.path.join(out_path, "oil_clean.csv"), index=False)
gold.to_csv(os.path.join(out_path, "gold_clean.csv"), index=False)
eurusd.to_csv(os.path.join(out_path, "eurusd_clean.csv"), index=False)

print("DONE ✔ cleaned market data saved")

