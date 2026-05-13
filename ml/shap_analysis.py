import pandas as pd
import shap
import matplotlib.pyplot as plt
from pathlib import Path
from xgboost import XGBClassifier

from ml.preprocessing import prepare_features, load_dataset

DATA_PATH = Path("paper_assets/03_metrics/metrics_ml_ready.csv")
OUTPUT_DIR = Path("paper_assets/05_experiments")


def run_shap_analysis():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_dataset(DATA_PATH)

    X, y = prepare_features(df)

    # Train XGBoost model
    model = XGBClassifier(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        random_state=42
    )

    model.fit(X, y)

    # SHAP explainer
    explainer = shap.TreeExplainer(model)

    shap_values = explainer.shap_values(X)

    # Summary Plot
    plt.figure()
    shap.summary_plot(shap_values, X, show=False)

    summary_path = OUTPUT_DIR / "shap_summary.png"

    plt.savefig(summary_path, bbox_inches="tight")
    plt.close()

    # Feature Importance Bar Plot
    plt.figure()
    shap.summary_plot(shap_values, X, plot_type="bar", show=False)

    bar_path = OUTPUT_DIR / "shap_feature_importance.png"

    plt.savefig(bar_path, bbox_inches="tight")
    plt.close()

    print("SHAP plots saved:")
    print(summary_path)
    print(bar_path)


if __name__ == "__main__":
    run_shap_analysis()