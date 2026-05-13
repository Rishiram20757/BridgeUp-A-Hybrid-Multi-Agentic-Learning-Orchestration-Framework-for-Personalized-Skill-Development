import pandas as pd

df = pd.read_csv("data/processed/D1_final.csv")

# --- normalize domain if missing ---
def infer_domain(row):
    if pd.notna(row["domain"]) and row["domain"].strip():
        return row["domain"]

    text = f"{row['title']} {row['skill_tags']}".lower()

    if any(x in text for x in ["data", "analytics", "machine learning"]):
        return "Data Science"
    if any(x in text for x in ["health", "clinical", "medical"]):
        return "Health"
    if any(x in text for x in ["cloud", "it", "google", "software"]):
        return "Information Technology"
    if any(x in text for x in ["climate", "sustainability", "environment"]):
        return "Sustainability"

    return "General"

df["domain"] = df.apply(infer_domain, axis=1)

# --- normalize skill tags ---
df["skill_tags"] = (
    df["skill_tags"]
    .fillna("")
    .str.lower()
    .str.replace(",", "|")
)

df.to_csv("data/processed/D1_final.csv", index=False)

print("✅ D1 normalized & updated")
