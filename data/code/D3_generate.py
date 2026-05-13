import pandas as pd
from pathlib import Path

# ---------- paths ----------
BASE_DIR = Path(__file__).resolve().parents[2]  # BridgeUp/
OUT_PATH = BASE_DIR / "data" / "processed" / "D3_skill_job_mapping.csv"

# ---------- D3 data ----------
data = [
    {
        "job_role_id": "J01",
        "job_role_name": "Software Engineer",
        "required_skills": "programming fundamentals|data structures|algorithms|object oriented programming|version control",
        "skill_weightage": "programming fundamentals:0.25|data structures:0.25|algorithms:0.2|object oriented programming:0.2|version control:0.1",
        "domain": "Programming"
    },
    {
        "job_role_id": "J02",
        "job_role_name": "Data Analyst",
        "required_skills": "python|sql|statistics|data visualization|excel",
        "skill_weightage": "python:0.25|sql:0.25|statistics:0.2|data visualization:0.2|excel:0.1",
        "domain": "Data Science"
    },
    {
        "job_role_id": "J03",
        "job_role_name": "Data Scientist",
        "required_skills": "python|statistics|machine learning basics|data analysis|data visualization",
        "skill_weightage": "python:0.25|statistics:0.25|machine learning basics:0.2|data analysis:0.15|data visualization:0.15",
        "domain": "Data Science"
    },
    {
        "job_role_id": "J04",
        "job_role_name": "Machine Learning Engineer",
        "required_skills": "python|machine learning basics|deep learning|linear algebra|model deployment",
        "skill_weightage": "python:0.25|machine learning basics:0.25|deep learning:0.2|linear algebra:0.15|model deployment:0.15",
        "domain": "Machine Learning"
    },
    {
        "job_role_id": "J05",
        "job_role_name": "Full Stack Developer",
        "required_skills": "html css|javascript|frontend frameworks|backend development|databases",
        "skill_weightage": "html css:0.2|javascript:0.25|frontend frameworks:0.2|backend development:0.2|databases:0.15",
        "domain": "Programming"
    },
    {
        "job_role_id": "J06",
        "job_role_name": "Backend Developer",
        "required_skills": "programming fundamentals|backend development|databases|api design|authentication",
        "skill_weightage": "programming fundamentals:0.25|backend development:0.3|databases:0.2|api design:0.15|authentication:0.1",
        "domain": "Programming"
    },
    {
        "job_role_id": "J07",
        "job_role_name": "Frontend Developer",
        "required_skills": "html css|javascript|responsive design|user interface design|frontend frameworks",
        "skill_weightage": "html css:0.25|javascript:0.3|responsive design:0.15|user interface design:0.15|frontend frameworks:0.15",
        "domain": "Programming"
    },
    {
        "job_role_id": "J08",
        "job_role_name": "DevOps Engineer",
        "required_skills": "linux|version control|ci cd|containerization|cloud fundamentals",
        "skill_weightage": "linux:0.2|version control:0.15|ci cd:0.25|containerization:0.2|cloud fundamentals:0.2",
        "domain": "DevOps"
    }
]

# ---------- create dataframe ----------
df = pd.DataFrame(data)

# ---------- save ----------
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT_PATH, index=False)

print("✅ D3_skill_job_mapping.csv created successfully")
print(df)
