import pandas as pd
from pathlib import Path

INPUT_PATH = Path("paper_assets/03_metrics/metrics_v1.csv")
OUTPUT_PATH = Path("paper_assets/03_metrics/metrics_ml_ready.csv")


def build_dataset():

    df = pd.read_csv(INPUT_PATH)

    # Binary label
    df["dropout_label"] = (df["dropoff_risk"] >= 0.3).astype(int)

    ml_df = df[
        [
            "strategy",
            "weekly_hours",
            "delay_index_hours",
            "workload_utilization",
            "stability_score",
            "consistency_score",
            "dropout_label"
        ]
    ]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    ml_df.to_csv(OUTPUT_PATH, index=False)

    print("ML dataset created:")
    print(OUTPUT_PATH)

    print("\nClass distribution:")
    print(ml_df["dropout_label"].value_counts())


if __name__ == "__main__":
    build_dataset()