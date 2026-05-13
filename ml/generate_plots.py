import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from ml.preprocessing import load_dataset, prepare_features


DATA_PATH = Path("paper_assets/03_metrics/metrics_ml_ready.csv")
OUTPUT_DIR = Path("paper_assets/05_experiments")


def generate_plots():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_dataset(DATA_PATH)

    X, y = prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=10,
        random_state=42
    )

    model.fit(X_train, y_train)

    # ------------------------------------------------
    # Confusion Matrix
    # ------------------------------------------------

    plt.figure()

    ConfusionMatrixDisplay.from_estimator(
        model,
        X_test,
        y_test
    )

    plt.title("Confusion Matrix")

    cm_path = OUTPUT_DIR / "confusion_matrix.png"

    plt.savefig(cm_path)

    plt.close()

    # ------------------------------------------------
    # ROC Curve
    # ------------------------------------------------

    plt.figure()

    RocCurveDisplay.from_estimator(
        model,
        X_test,
        y_test
    )

    plt.title("ROC Curve")

    roc_path = OUTPUT_DIR / "roc_curve.png"

    plt.savefig(roc_path)

    plt.close()

    # ------------------------------------------------
    # Feature Importance
    # ------------------------------------------------

    importances = model.feature_importances_

    feature_names = X.columns

    plt.figure(figsize=(8,5))

    plt.bar(feature_names, importances)

    plt.xticks(rotation=45)

    plt.title("Feature Importance")

    plt.tight_layout()

    fi_path = OUTPUT_DIR / "feature_importance.png"

    plt.savefig(fi_path)

    plt.close()

    print("Plots saved:")
    print(cm_path)
    print(roc_path)
    print(fi_path)


if __name__ == "__main__":
    generate_plots()