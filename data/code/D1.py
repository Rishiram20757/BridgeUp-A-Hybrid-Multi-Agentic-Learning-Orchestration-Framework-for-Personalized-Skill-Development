import pandas as pd
import re
from pathlib import Path

# --- paths ---
BASE_DIR = Path(__file__).resolve().parents[2]   # BridgeUp/
RAW_PATH = BASE_DIR / "data" / "raw" / "D1_kaggle_raw.csv"
OUT_PATH = BASE_DIR / "data" / "processed" / "D1_final.csv"

# --- load raw data ---
df = pd.read_csv(RAW_PATH)

# keep only columns that actually contain data
df = df[
    ["Title", "URL", "Category", "Skills", "Duration", "Site"]
]

df = df.dropna(subset=["Title", "URL"])

# rename columns to BridgeUp schema
df = df.rename(columns={
    "Title": "title",
    "URL": "url",
    "Category": "domain",
    "Skills": "skill_tags",
    "Duration": "duration_raw",
    "Site": "provider"
})

# --- duration parsing ---
def parse_duration(val):
    if pd.isna(val):
        return None
    val = str(val).lower()
    nums = re.findall(r"\d+", val)
    return int(nums[0]) if nums else None

df["duration_hours"] = df["duration_raw"].apply(parse_duration)

# --- difficulty inference ---
def infer_difficulty(row):
    text = f"{row['title']} {row['skill_tags']}".lower()
    if any(x in text for x in ["beginner", "intro", "basic"]):
        return "Beginner"
    if any(x in text for x in ["advanced", "deep learning"]):
        return "Advanced"
    return "Intermediate"

df["difficulty"] = df.apply(infer_difficulty, axis=1)

# --- static fields ---
df["format"] = "Video"
df["cost_type"] = "Paid"

# --- generate IDs ---
df = df.reset_index(drop=True)
df["resource_id"] = df.index.map(lambda i: f"R{i+1:03d}")

# --- reorder to final schema ---
final_df = df[
    [
        "resource_id",
        "title",
        "provider",
        "domain",
        "skill_tags",
        "difficulty",
        "duration_hours",
        "format",
        "cost_type",
        "url"
    ]
]

# --- sample to manageable size ---
final_df = final_df.sample(n=min(120, len(final_df)), random_state=42)

# --- save ---
final_df.to_csv(OUT_PATH, index=False)

print("✅ D1_final.csv created")
print("Rows:", len(final_df))
print(final_df.head())
