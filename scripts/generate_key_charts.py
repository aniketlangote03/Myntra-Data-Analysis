"""Generate key charts for the images/ folder (run after data cleaning)."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "myntra_cleaned.csv"
OUT = ROOT / "images"
OUT.mkdir(exist_ok=True)

plt.style.use("ggplot")


def main() -> None:
    df = pd.read_csv(DATA)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df["price"], bins=50, kde=True, ax=ax)
    ax.set_title("Price Distribution — Men's Jeans on Myntra")
    ax.set_xlabel("Price (₹)")
    fig.tight_layout()
    fig.savefig(OUT / "price_distribution.png", dpi=120)
    plt.close(fig)

    top_brands = (
        df.groupby("brand_name")["number_of_ratings"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    top_brands.sort_values().plot(kind="barh", ax=ax, color="#E62E5C")
    ax.set_title("Top 10 Brands by Total Customer Ratings")
    ax.set_xlabel("Total Ratings")
    fig.tight_layout()
    fig.savefig(OUT / "top_brands_engagement.png", dpi=120)
    plt.close(fig)

    bins = [0, 500, 1000, 2000, 5000, float("inf")]
    labels = ["≤₹500", "₹501–1000", "₹1001–2000", "₹2001–5000", ">₹5000"]
    df["price_segment"] = pd.cut(df["price"], bins=bins, labels=labels)
    segment_counts = df["price_segment"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    segment_counts.plot(kind="bar", ax=ax, color="#2E86AB")
    ax.set_title("Products by Price Segment")
    ax.set_ylabel("Product Count")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(OUT / "price_segments.png", dpi=120)
    plt.close(fig)

    print(f"Saved charts to {OUT}/")


if __name__ == "__main__":
    main()
