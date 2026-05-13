import joblib
import numpy as np


MODEL_PATH = "models/bridgeup_dropout_model.pkl"


def load_model():

    data = joblib.load(MODEL_PATH)

    return data["model"], data["scaler"]


def predict(metrics):

    model, scaler = load_model()

    features = np.array([
        metrics["completion_rate"],
        metrics["delay_index_hours"],
        metrics["workload_utilization"],
        metrics["stability_score"],
        metrics["consistency_score"]
    ]).reshape(1, -1)

    features_scaled = scaler.transform(features)

    probability = model.predict_proba(features_scaled)[0][1]

    return probability