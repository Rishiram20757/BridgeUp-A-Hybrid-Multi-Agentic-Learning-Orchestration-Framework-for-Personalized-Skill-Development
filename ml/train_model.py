import joblib
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from ml.preprocessing import (
    load_dataset,
    prepare_features,
    scale_features,
    split_dataset
)


DATA_PATH = Path("paper_assets/03_metrics/metrics_ml_ready.csv")
MODEL_PATH = Path("models/bridgeup_dropout_model.pkl")


def train_models():

    df = load_dataset(DATA_PATH)

    X, y = prepare_features(df)

    X_scaled, scaler = scale_features(X)

    X_train, X_test, y_train, y_test = split_dataset(X_scaled, y)

    # Logistic Regression
    log_model = LogisticRegression(
        C=0.5,
        max_iter=300
    )

    log_model.fit(X_train, y_train)

    # Random Forest
    rf_model = RandomForestClassifier(
        n_estimators=400,
        max_depth=10,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42
    )

    rf_model.fit(X_train, y_train)

    # XGBoost
    xgb_model = XGBClassifier(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        random_state=42
    )

    xgb_model.fit(X_train, y_train)

    return log_model, rf_model, xgb_model, X_test, y_test, scaler


def save_model(model, scaler):

    MODEL_PATH.parent.mkdir(exist_ok=True)

    joblib.dump(
        {
            "model": model,
            "scaler": scaler
        },
        MODEL_PATH
    )


if __name__ == "__main__":

    log_model, rf_model, xgb_model, X_test, y_test, scaler = train_models()

    # save best model
    save_model(xgb_model, scaler)

    print("Model saved to models/bridgeup_dropout_model.pkl")