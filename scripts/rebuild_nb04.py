"""Rebuild NB4 as a lean EDA notebook (~50-70 cells, one round of business questions)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB_PATH = ROOT / "notebooks" / "04_Exploratory_Data_Analysis.ipynb"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [text]}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {},
        "source": [text],
        "outputs": [],
        "execution_count": None,
    }


def build_notebook() -> dict:
    cells = [
        md(
            "# Exploratory Data Analysis (EDA)\n\n"
            "## Scope of This Notebook\n\n"
            "This notebook performs **univariate and bivariate exploration** — understanding "
            "distributions, segments, and relationships in the cleaned dataset.\n\n"
            "Unlike **Notebook 5 (Advanced Business Insights)**, which builds composite scores "
            "for brand prioritization, EDA focuses on *what the data looks like* before "
            "deriving actionable rankings.\n\n"
            "**Input:** `data/myntra_cleaned.csv` (31,527 products after deduplication and "
            "discount-format cleaning)"
        ),
        md(
            "## Business Questions\n\n"
            "1. What is the price distribution of men's jeans on Myntra?\n"
            "2. Which brands have the highest average prices?\n"
            "3. How do customer ratings vary across price segments?\n"
            "4. Which brands dominate the budget segment?\n"
            "5. How are products distributed across price categories?"
        ),
        md("## Setup"),
        code(
            "import pandas as pd\n"
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n\n"
            "plt.style.use('ggplot')\n"
            "sns.set_palette('husl')\n"
        ),
        code('df = pd.read_csv("../data/myntra_cleaned.csv")\ndf.head()'),
        code(
            "summary = {\n"
            '    "total_products": len(df),\n'
            '    "unique_brands": df["brand_name"].nunique(),\n'
            '    "avg_price": df["price"].mean(),\n'
            '    "median_price": df["price"].median(),\n'
            '    "avg_rating": df["ratings"].mean(),\n'
            '    "avg_discount_pct": df["discount_percent"].mean() * 100,\n'
            "}\n"
            'print("Dataset Summary:")\n'
            "for k, v in summary.items():\n"
            '    if isinstance(v, float):\n'
            '        print(f"  {k}: {v:,.2f}")\n'
            "    else:\n"
            '        print(f"  {k}: {v:,}")'
        ),
        md("---\n\n## BQ1 — Price Distribution\n\nWhat is the price distribution of men's jeans on Myntra?"),
        code('df["price"].describe()'),
        code(
            "plt.figure(figsize=(10, 6))\n"
            'sns.histplot(df["price"], bins=50, kde=True, color="#E62E5C")\n'
            'plt.title("Distribution of Product Selling Prices")\n'
            'plt.xlabel("Price (₹)")\n'
            'plt.ylabel("Number of Products")\n'
            "plt.tight_layout()\n"
            'plt.savefig("../images/eda_price_distribution.png", dpi=120, bbox_inches="tight")\n'
            "plt.show()"
        ),
        md(
            "### Observation & Insight\n\n"
            "The price distribution is **right-skewed**: the median (₹1,484) sits below the mean "
            "(₹1,697), driven by a long tail of premium and luxury items. Most products cluster "
            "in the mid-range segment, which is typical for mass-market fashion e-commerce."
        ),
        md("## BQ2 — Highest-Priced Brands\n\nWhich brands have the highest average prices?"),
        code(
            "brand_avg_price = (\n"
            '    df.groupby("brand_name")["price"]\n'
            "    .mean()\n"
            "    .sort_values(ascending=False)\n"
            "    .head(10)\n"
            ")\n"
            "brand_avg_price"
        ),
        code(
            "plt.figure(figsize=(10, 6))\n"
            "sns.barplot(x=brand_avg_price.values, y=brand_avg_price.index, color='darkorange')\n"
            'plt.title("Top 10 Brands by Average Price")\n'
            'plt.xlabel("Average Price (₹)")\n'
            "plt.tight_layout()\n"
            'plt.savefig("../images/eda_top_brands_price.png", dpi=120, bbox_inches="tight")\n'
            "plt.show()"
        ),
        md(
            "### Observation & Insight\n\n"
            "Premium and designer labels dominate the highest average-price tier. These brands "
            "serve a niche luxury segment and should be merchandised separately from mass-market "
            "offerings."
        ),
        md("## BQ3 — Ratings Across Price Segments\n\nHow do customer ratings vary across price segments?"),
        code(
            'PRICE_BINS = [0, 500, 1000, 2000, 5000, float("inf")]\n'
            'PRICE_LABELS = ["≤₹500", "₹501–1000", "₹1001–2000", "₹2001–5000", ">₹5000"]\n\n'
            'df["price_segment"] = pd.cut(df["price"], bins=PRICE_BINS, labels=PRICE_LABELS)\n'
            "segment_rating = (\n"
            '    df.groupby("price_segment", observed=True)["ratings"]\n'
            "    .agg(['mean', 'count'])\n"
            "    .round(2)\n"
            ")\n"
            "segment_rating"
        ),
        code(
            "plt.figure(figsize=(10, 6))\n"
            'sns.boxplot(data=df, x="price_segment", y="ratings", palette="Blues")\n'
            'plt.title("Customer Ratings by Price Segment")\n'
            'plt.xlabel("Price Segment")\n'
            'plt.ylabel("Rating (1–5)")\n'
            "plt.xticks(rotation=30)\n"
            "plt.tight_layout()\n"
            'plt.savefig("../images/eda_ratings_by_segment.png", dpi=120, bbox_inches="tight")\n'
            "plt.show()"
        ),
        md(
            "### Observation & Insight\n\n"
            "Ratings are relatively stable across segments, with a slight uplift in premium tiers. "
            "The **₹1,001–2,000 segment** combines high volume with solid ratings — the core "
            "commercial sweet spot."
        ),
        md("## BQ4 — Budget Segment Leaders\n\nWhich brands dominate the budget segment?"),
        code(
            'budget = df[df["price_segment"] == "≤₹500"]\n'
            "budget_brands = (\n"
            '    budget.groupby("brand_name")\n'
            '    .agg(products=("price", "count"), avg_price=("price", "mean"))\n'
            "    .sort_values('products', ascending=False)\n"
            "    .head(10)\n"
            "    .round(2)\n"
            ")\n"
            "budget_brands"
        ),
        code(
            "plt.figure(figsize=(10, 6))\n"
            "top_budget = budget_brands['products'].sort_values()\n"
            "plt.barh(top_budget.index, top_budget.values, color='steelblue')\n"
            'plt.title("Top 10 Brands in Budget Segment (≤₹500)")\n'
            'plt.xlabel("Number of Products")\n'
            "plt.tight_layout()\n"
            'plt.savefig("../images/eda_budget_brands.png", dpi=120, bbox_inches="tight")\n'
            "plt.show()"
        ),
        md(
            "### Observation & Insight\n\n"
            "A handful of value-oriented brands account for most budget listings. Myntra can "
            "use this segment for acquisition campaigns and entry-level customer onboarding."
        ),
        md("## BQ5 — Price Category Distribution\n\nHow are products distributed across price categories?"),
        code(
            'CATEGORY_BINS = [0, 1000, 2000, 3000, 5000, 60000]\n'
            'CATEGORY_LABELS = ["Budget", "Economy", "Mid-Range", "Premium", "Luxury"]\n\n'
            'df["price_category"] = pd.cut(\n'
            '    df["price"], bins=CATEGORY_BINS, labels=CATEGORY_LABELS\n'
            ")\n"
            "category_counts = df['price_category'].value_counts().reindex(CATEGORY_LABELS)\n"
            "category_counts"
        ),
        code(
            "plt.figure(figsize=(9, 6))\n"
            "sns.countplot(data=df, x='price_category', order=CATEGORY_LABELS, color='#2E86AB')\n"
            'plt.title("Product Distribution by Price Category")\n'
            'plt.xlabel("Price Category")\n'
            'plt.ylabel("Number of Products")\n'
            "plt.tight_layout()\n"
            'plt.savefig("../images/eda_price_categories.png", dpi=120, bbox_inches="tight")\n'
            "plt.show()"
        ),
        md(
            "### Observation & Insight\n\n"
            "The catalog is concentrated in **Economy and Mid-Range** categories. Luxury "
            "represents a small fraction but extends the price range significantly."
        ),
        md("---\n\n## Supplementary — Brand Engagement & Discounts"),
        md("### Top Brands by Customer Engagement"),
        code(
            "brand_engagement = (\n"
            '    df.groupby("brand_name")\n'
            "    .agg(\n"
            '        products=("price", "count"),\n'
            '        total_ratings=("number_of_ratings", "sum"),\n'
            '        avg_rating=("ratings", "mean"),\n'
            "    )\n"
            "    .sort_values('total_ratings', ascending=False)\n"
            "    .head(10)\n"
            "    .round(2)\n"
            ")\n"
            "brand_engagement"
        ),
        code(
            "top = brand_engagement.sort_values('total_ratings')\n"
            "plt.figure(figsize=(10, 6))\n"
            "plt.barh(top.index, top['total_ratings'], color='crimson')\n"
            'plt.title("Top 10 Brands by Total Customer Ratings")\n'
            'plt.xlabel("Total Ratings")\n'
            "plt.tight_layout()\n"
            'plt.savefig("../images/eda_brand_engagement.png", dpi=120, bbox_inches="tight")\n'
            "plt.show()"
        ),
        md("### Discount Distribution"),
        code(
            'print(f"Average discount: {df[\'discount_percent\'].mean() * 100:.1f}%")\n'
            'print(f"Median discount:  {df[\'discount_percent\'].median() * 100:.1f}%")'
        ),
        code(
            "plt.figure(figsize=(10, 6))\n"
            'sns.histplot(df["discount_percent"] * 100, bins=30, kde=True, color="darkorange")\n'
            'plt.title("Discount Percentage Distribution")\n'
            'plt.xlabel("Discount (%)")\n'
            "plt.tight_layout()\n"
            'plt.savefig("../images/eda_discount_distribution.png", dpi=120, bbox_inches="tight")\n'
            "plt.show()"
        ),
        md("### Price vs. Rating Correlation"),
        code(
            'corr = df["price"].corr(df["ratings"])\n'
            'print(f"Price–Rating correlation: {corr:.3f}")'
        ),
        code(
            "plt.figure(figsize=(10, 6))\n"
            'sns.scatterplot(data=df.sample(min(5000, len(df)), x="price", y="ratings", alpha=0.3)\n'
            'plt.title("Price vs. Customer Rating")\n'
            'plt.xlabel("Price (₹)")\n'
            'plt.ylabel("Rating (1–5)")\n'
            "plt.tight_layout()\n"
            'plt.savefig("../images/eda_price_rating_scatter.png", dpi=120, bbox_inches="tight")\n'
            "plt.show()"
        ),
        md(
            "---\n\n"
            "## EDA Conclusions\n\n"
            "- **Pricing:** Mid-range (₹1,001–2,000) is the commercial core; distribution is right-skewed.\n"
            "- **Brands:** Roadster, HIGHLANDER, and value labels lead engagement; premium brands anchor the top price tier.\n"
            "- **Ratings:** Stable across segments; no strong price–rating linear relationship.\n"
            "- **Discounts:** Average ~50% off; heavy promotional activity across the catalog.\n\n"
            "→ Proceed to **Notebook 5** for composite Value Score and Business Performance Score rankings."
        ),
    ]
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.12.0"},
        },
        "cells": cells,
    }


def main() -> None:
    nb = build_notebook()
    NB_PATH.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Rebuilt {NB_PATH.name}: {len(nb['cells'])} cells")


if __name__ == "__main__":
    main()
