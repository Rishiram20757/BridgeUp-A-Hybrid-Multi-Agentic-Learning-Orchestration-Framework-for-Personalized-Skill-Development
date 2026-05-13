import pandas as pd

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from ml.preprocessing import load_dataset, prepare_features, scale_features


DATA_PATH = "paper_assets/03_metrics/metrics_ml_ready.csv"


def evaluate():

    df = load_dataset(DATA_PATH)

    X, y = prepare_features(df)

    X_scaled, scaler = scale_features(X)

    models = {

        "Logistic Regression": LogisticRegression(
            C=0.5,
            max_iter=300
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=400,
            max_depth=10,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42
        ),

        "XGBoost": XGBClassifier(
            n_estimators=400,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=42
        )
    }

    skf = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    results = []

    for name, model in models.items():

        scores = cross_validate(
            model,
            X_scaled,
            y,
            cv=skf,
            scoring=[
                "accuracy",
                "precision",
                "recall",
                "f1",
                "roc_auc"
            ]
        )

        results.append({
            "Model": name,
            "Accuracy": scores["test_accuracy"].mean(),
            "Precision": scores["test_precision"].mean(),
            "Recall": scores["test_recall"].mean(),
            "F1": scores["test_f1"].mean(),
            "ROC_AUC": scores["test_roc_auc"].mean()
        })

    df_results = pd.DataFrame(results)

    print("\nCross-Validated Model Performance:\n")

    print(df_results)


if __name__ == "__main__":
    evaluate()