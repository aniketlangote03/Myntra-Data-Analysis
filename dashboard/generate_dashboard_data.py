"""Generate dashboard_data.json from myntra_cleaned.csv.

Reads the cleaned Myntra dataset and produces a JSON file that the
HTML dashboard (index.html) loads via fetch() to populate KPIs,
Plotly charts, and data tables with real values.

Usage:
    python dashboard/generate_dashboard_data.py
"""

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "myntra_cleaned.csv"
OUTPUT_PATH = Path(__file__).resolve().parent / "dashboard_data.json"

# Price band definitions (matching the dashboard layout)
PRICE_BANDS = [
    ("Under ₹1,000", 0, 999),
    ("₹1,000–₹1,999", 1000, 1999),
    ("₹2,000–₹2,999", 2000, 2999),
    ("₹3,000+", 3000, float("inf")),
]

# Scatter‑plot sample size
SCATTER_SAMPLE = 2000

# Box‑plot sample per band (keeps the HTML performant)
BOX_SAMPLE_PER_BAND = 500


def _safe(v):
    """Convert numpy types to JSON-serialisable Python types."""
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        if math.isnan(v) or math.isinf(v):
            return None
        return round(float(v), 2)
    return v


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    # --- Derived columns ------------------------------------------------
    # discount_percent is stored as 0–1; create a percentage column
    df["discount_pct"] = df["discount_percent"] * 100

    # Assign each row to a price band
    conditions = [
        df["price"] < 1000,
        (df["price"] >= 1000) & (df["price"] < 2000),
        (df["price"] >= 2000) & (df["price"] < 3000),
        df["price"] >= 3000,
    ]
    band_labels = [b[0] for b in PRICE_BANDS]
    df["price_band"] = np.select(conditions, band_labels, default="Other")

    # --- 1. KPI values ---------------------------------------------------
    kpis = {
        "total_products": int(len(df)),
        "total_brands": int(df["brand_name"].nunique()),
        "avg_price": round(float(df["price"].mean()), 0),
        "median_price": round(float(df["price"].median()), 0),
        "avg_discount_pct": round(float(df["discount_pct"].mean()), 1),
        "avg_rating": round(float(df["ratings"].mean()), 2),
        "total_reviews": int(df["number_of_ratings"].sum()),
    }

    # --- 2. Price distribution (all prices, as integers) -----------------
    price_distribution = sorted(df["price"].dropna().astype(int).tolist())

    # --- 3. Top 15 brands by product count -------------------------------
    brand_counts = (
        df.groupby("brand_name")
        .agg(
            products=("price", "count"),
            avg_rating=("ratings", "mean"),
        )
        .reset_index()
        .nlargest(15, "products")
        .sort_values("products", ascending=True)
    )
    top_brands = {
        "names": brand_counts["brand_name"].tolist(),
        "counts": brand_counts["products"].tolist(),
        "ratings": [round(r, 2) for r in brand_counts["avg_rating"].tolist()],
    }

    # --- 4. Product mix by price band ------------------------------------
    mix = (
        df.groupby("price_band")
        .agg(
            products=("price", "count"),
            avg_discount=("discount_pct", "mean"),
        )
        .reindex(band_labels)
        .reset_index()
    )
    price_mix = {
        "bands": mix["price_band"].tolist(),
        "counts": [int(c) for c in mix["products"].tolist()],
        "avg_discount": [round(d, 2) for d in mix["avg_discount"].tolist()],
    }

    # --- 5. Discount box plot (sampled per band) -------------------------
    discount_box = {}
    for label, lo, hi in PRICE_BANDS:
        band_df = df[(df["price"] >= lo) & (df["price"] <= hi)] if hi != float("inf") else df[df["price"] >= lo]
        vals = band_df["discount_pct"].dropna()
        if len(vals) > BOX_SAMPLE_PER_BAND:
            vals = vals.sample(BOX_SAMPLE_PER_BAND, random_state=42)
        discount_box[label] = [round(v, 1) for v in vals.tolist()]

    # --- 6. Top 10 brands by average rating (min 20 products) ------------
    brand_rating = (
        df.groupby("brand_name")
        .agg(
            products=("price", "count"),
            avg_rating=("ratings", "mean"),
        )
        .reset_index()
    )
    brand_rating = brand_rating[brand_rating["products"] >= 20]
    brand_rating_top = (
        brand_rating.nlargest(10, "avg_rating")
        .sort_values("avg_rating", ascending=True)
    )
    top_brands_by_rating = {
        "names": brand_rating_top["brand_name"].tolist(),
        "ratings": [round(r, 2) for r in brand_rating_top["avg_rating"].tolist()],
        "counts": brand_rating_top["products"].tolist(),
    }

    # --- 7. Scatter plot (sampled) ---------------------------------------
    scatter_df = df.dropna(subset=["price", "ratings", "discount_pct", "number_of_ratings"])
    if len(scatter_df) > SCATTER_SAMPLE:
        scatter_df = scatter_df.sample(SCATTER_SAMPLE, random_state=42)

    scatter = {
        "prices": [int(p) for p in scatter_df["price"].tolist()],
        "ratings": [round(r, 1) for r in scatter_df["ratings"].tolist()],
        "discount_pct": [round(d, 1) for d in scatter_df["discount_pct"].tolist()],
        "num_ratings": [int(n) for n in scatter_df["number_of_ratings"].tolist()],
        "brands": scatter_df["brand_name"].tolist(),
        "descriptions": scatter_df["pants_description"].tolist(),
        "mrp": [int(m) for m in scatter_df["MRP"].tolist()],
    }

    # --- 8. Brand performance table (top 12 by product count) ------------
    brand_perf = (
        df.groupby("brand_name")
        .agg(
            products=("price", "count"),
            avg_price=("price", "mean"),
            avg_discount=("discount_pct", "mean"),
            avg_rating=("ratings", "mean"),
            total_reviews=("number_of_ratings", "sum"),
        )
        .reset_index()
        .nlargest(12, "products")
        .sort_values("products", ascending=False)
    )
    brand_table = []
    for _, row in brand_perf.iterrows():
        brand_table.append({
            "brand": row["brand_name"],
            "products": int(row["products"]),
            "avg_price": round(float(row["avg_price"]), 0),
            "avg_discount": round(float(row["avg_discount"]), 1),
            "avg_rating": round(float(row["avg_rating"]), 2),
            "total_reviews": int(row["total_reviews"]),
        })

    # --- 9. Top‑rated products (rating ≥ 4.3, reviews ≥ 100) ------------
    top_prods = (
        df[(df["ratings"] >= 4.3) & (df["number_of_ratings"] >= 100)]
        .sort_values(["ratings", "number_of_ratings"], ascending=[False, False])
        .head(12)
    )
    top_products = []
    for _, row in top_prods.iterrows():
        top_products.append({
            "brand": row["brand_name"],
            "description": row["pants_description"],
            "price": int(row["price"]),
            "discount_pct": round(float(row["discount_pct"]), 1),
            "rating": round(float(row["ratings"]), 1),
            "num_ratings": int(row["number_of_ratings"]),
        })

    # --- Assemble and write ----------------------------------------------
    dashboard_data = {
        "kpis": kpis,
        "price_distribution": price_distribution,
        "top_brands": top_brands,
        "price_mix": price_mix,
        "discount_box": discount_box,
        "top_brands_by_rating": top_brands_by_rating,
        "scatter": scatter,
        "brand_table": brand_table,
        "top_products": top_products,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, ensure_ascii=False)

    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"[OK] Generated {OUTPUT_PATH.relative_to(ROOT)}  ({size_kb:.0f} KB)")
    print(f"   Products : {kpis['total_products']:,}")
    print(f"   Brands   : {kpis['total_brands']}")
    print(f"   Avg Price: INR {kpis['avg_price']:,.0f}")
    print(f"   Avg Disc : {kpis['avg_discount_pct']}%")
    print(f"   Avg Rate : {kpis['avg_rating']}")
    print(f"   Reviews  : {kpis['total_reviews']:,}")


if __name__ == "__main__":
    main()
