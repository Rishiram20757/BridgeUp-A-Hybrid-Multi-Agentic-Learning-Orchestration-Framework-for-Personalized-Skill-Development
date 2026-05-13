import pandas as pd
from pathlib import Path

# ---------- paths ----------
BASE_DIR = Path(__file__).resolve().parents[2]
D2_PATH = BASE_DIR / "data" / "processed" / "D2_skill_domain_taxonomy.csv"
OUT_PATH = BASE_DIR / "data" / "processed" / "D4_skill_prerequisites.csv"

# ---------- load D2 ----------
df = pd.read_csv(D2_PATH)

skill_to_id = dict(zip(df["skill_name"], df["skill_id"]))

# ---------- dependency classification ----------
def classify_dependency(parent, child):
    parent = parent.lower()
    child = child.lower()

    # HARD dependencies
    if "fundamentals" in parent:
        return "hard"
    if parent == "statistics" and "machine learning" in child:
        return "hard"
    if "machine learning basics" in parent and "deep learning" in child:
        return "hard"
    if "data structures" in parent and "algorithms" in child:
        return "hard"

    # SOFT dependencies
    if parent == "version control" and "ci cd" in child:
        return "soft"
    if parent == "linux" and "container" in child:
        return "soft"
    if parent == "javascript" and "frontend" in child:
        return "soft"
    if "data analysis" in parent and "visualization" in child:
        return "soft"

    # default
    return "soft"


rows = []

for _, row in df.iterrows():
    if pd.notna(row["parent_skill"]) and row["parent_skill"].strip():
        child_id = row["skill_id"]
        parent_name = row["parent_skill"].strip()

        parent_id = skill_to_id.get(parent_name)
        if parent_id:
            dep_type = classify_dependency(parent_name, row["skill_name"])
            rows.append({
                "skill_id": child_id,
                "prerequisite_skill_id": parent_id,
                "dependency_type": dep_type
            })

out_df = pd.DataFrame(rows)
out_df.to_csv(OUT_PATH, index=False)

print("✅ D4_skill_prerequisites.csv regenerated")
print("Total dependencies:", len(out_df))
print(out_df["dependency_type"].value_counts())
print(out_df.head())
