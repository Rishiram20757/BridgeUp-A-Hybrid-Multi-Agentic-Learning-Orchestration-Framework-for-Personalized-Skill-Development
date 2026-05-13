import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = Path("paper_assets/03_metrics/metrics_ml_ready.csv")

OUTPUT_DIR = Path("paper_assets/05_experiments")
OUTPUT_FILE = OUTPUT_DIR / "correlation_heatmap.png"


def generate_heatmap():

    df = pd.read_csv(DATA_PATH)

    corr = df.corr(numeric_only=True)

    plt.figure(figsize=(8,6))

    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        fmt=".2f"
    )

    plt.title("Correlation Matrix of Monitoring Metrics")

    plt.tight_layout()

    # ensure directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    plt.savefig(OUTPUT_FILE)

    print("Heatmap saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    generate_heatmap()