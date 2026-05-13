import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def load_dataset(csv_path):
    df = pd.read_csv(csv_path)
    return df


def prepare_features(df):

    df = df.copy()

    # Encode strategy
    df["strategy"] = df["strategy"].map({
        "fast": 0,
        "balanced": 1,
        "deep": 2
    })

    # Interaction features (improves model)
    df["delay_workload"] = df["delay_index_hours"] * df["workload_utilization"]
    df["stability_consistency"] = df["stability_score"] * df["consistency_score"]

    feature_cols = [
        "strategy",
        "weekly_hours",
        "delay_index_hours",
        "workload_utilization",
        "stability_score",
        "consistency_score",
        "delay_workload",
        "stability_consistency"
    ]

    X = df[feature_cols]

    y = df["dropout_label"]

    return X, y


def scale_features(X):

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    return X_scaled, scaler


def split_dataset(X, y):

    return train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )