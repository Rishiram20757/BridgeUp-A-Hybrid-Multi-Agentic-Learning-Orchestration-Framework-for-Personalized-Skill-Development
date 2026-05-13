import pandas as pd
from pathlib import Path

# ---------- paths ----------
BASE_DIR = Path(__file__).resolve().parents[2]
D1_PATH = BASE_DIR / "data" / "processed" / "D1_final.csv"
D3_PATH = BASE_DIR / "data" / "processed" / "D3_skill_job_mapping.csv"
OUT_PATH = BASE_DIR / "data" / "processed" / "D2_skill_domain_taxonomy.csv"

# ---------- load data ----------
d1 = pd.read_csv(D1_PATH)
d3 = pd.read_csv(D3_PATH)

# ---------- collect skills ----------
skills = set()

# from D3
for s in d3["required_skills"]:
    for sk in s.split("|"):
        skills.add(sk.strip().lower())

# from D1
for s in d1["skill_tags"].dropna():
    for sk in s.split("|"):
        if sk.strip():
            skills.add(sk.strip().lower())

skills = sorted(skills)

# ---------- domain inference ----------
def infer_domain(skill):
    if any(x in skill for x in ["data", "sql", "statistics", "analysis", "visualization"]):
        return "Data Science"
    if any(x in skill for x in ["machine learning", "deep learning", "model"]):
        return "Machine Learning"
    if any(x in skill for x in ["html", "css", "javascript", "frontend", "backend", "api"]):
        return "Programming"
    if any(x in skill for x in ["linux", "ci cd", "container", "cloud", "devops"]):
        return "DevOps"
    return "General"

# ---------- level inference ----------
def infer_level(skill):
    if any(x in skill for x in ["fundamentals", "basics", "intro"]):
        return "Beginner"
    if any(x in skill for x in ["advanced", "deep learning"]):
        return "Advanced"
    return "Intermediate"

# ---------- parent skill mapping ----------
parent_map = {
    "algorithms": "data structures",
    "deep learning": "machine learning basics",
    "machine learning basics": "statistics",
    "data visualization": "data analysis",
    "frontend frameworks": "javascript",
    "backend development": "programming fundamentals",
    "api design": "backend development",
    "containerization": "linux",
    "ci cd": "version control"
}

# ---------- build D2 ----------
rows = []
for idx, skill in enumerate(skills, start=1):
    rows.append({
        "skill_id": f"S{idx:03d}",
        "skill_name": skill,
        "domain": infer_domain(skill),
        "parent_skill": parent_map.get(skill, ""),
        "level": infer_level(skill),
        "description": f"Knowledge or competency in {skill}"
    })

df = pd.DataFrame(rows)

# ---------- save ----------
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT_PATH, index=False)

print("✅ D2_skill_domain_taxonomy.csv created")
print("Total skills:", len(df))
print(df.head())
