"""Interactive Streamlit dashboard for Myntra Men's Jeans analysis."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "myntra_cleaned.csv"

PRICE_BINS = [0, 500, 1000, 2000, 5000, float("inf")]
PRICE_LABELS = ["≤₹500", "₹501–1000", "₹1001–2000", "₹2001–5000", ">₹5000"]


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["price_segment"] = pd.cut(df["price"], bins=PRICE_BINS, labels=PRICE_LABELS)
    return df


def brand_metrics(df: pd.DataFrame) -> pd.DataFrame:
    brand = (
        df.groupby("brand_name")
        .agg(
            product_count=("price", "count"),
            avg_price=("price", "mean"),
            avg_discount=("discount_percent", "mean"),
            avg_rating=("ratings", "mean"),
            total_ratings=("number_of_ratings", "sum"),
        )
        .reset_index()
    )
    brand["ratings_per_product"] = brand["total_ratings"] / brand["product_count"]

    brand["rating_score"] = brand["avg_rating"] / brand["avg_rating"].max()
    brand["discount_score"] = brand["avg_discount"] / brand["avg_discount"].max()
    brand["price_score"] = brand["avg_price"].min() / brand["avg_price"]
    brand["value_score"] = (
        0.40 * brand["rating_score"]
        + 0.30 * brand["discount_score"]
        + 0.30 * brand["price_score"]
    )

    for col in ["avg_rating", "ratings_per_product", "value_score", "avg_discount"]:
        brand[f"{col}_norm"] = (brand[col] - brand[col].min()) / (
            brand[col].max() - brand[col].min()
        )

    brand["business_performance_score"] = (
        0.35 * brand["avg_rating_norm"]
        + 0.30 * brand["ratings_per_product_norm"]
        + 0.20 * brand["value_score_norm"]
        + 0.15 * brand["avg_discount_norm"]
    )
    return brand.sort_values("business_performance_score", ascending=False)


def main() -> None:
    st.set_page_config(
        page_title="Myntra Jeans Analytics",
        page_icon="👖",
        layout="wide",
    )

    df = load_data()
    brands = brand_metrics(df)

    st.title("Myntra Men's Jeans — Analytics Dashboard")
    st.caption(
        f"{len(df):,} products · {df['brand_name'].nunique()} brands · "
        "Interactive exploration of pricing, ratings, and brand performance"
    )

    with st.sidebar:
        st.header("Filters")
        min_products = st.slider("Min products per brand", 1, 50, 20)
        st.caption("Default: ≥ 20 products for sample size reliability (matches Notebook 5).")
        selected_segments = st.multiselect(
            "Price segment",
            options=PRICE_LABELS,
            default=list(PRICE_LABELS),
        )
        top_n = st.slider("Top N brands", 5, 20, 10)

    filtered = df[df["price_segment"].isin(selected_segments)]
    brand_filtered = brands[brands["product_count"] >= min_products]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Products", f"{len(filtered):,}")
    col2.metric("Avg Price", f"₹{filtered['price'].mean():,.0f}")
    col3.metric("Avg Rating", f"{filtered['ratings'].mean():.2f}")
    col4.metric("Avg Discount", f"{filtered['discount_percent'].mean() * 100:.0f}%")

    tab1, tab2, tab3 = st.tabs(["Overview", "Brand Rankings", "Price Segments"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            fig_price = px.histogram(
                filtered,
                x="price",
                nbins=50,
                title="Price Distribution",
                labels={"price": "Price (₹)"},
                color_discrete_sequence=["#E62E5C"],
            )
            st.plotly_chart(fig_price, use_container_width=True)
        with c2:
            seg_counts = filtered["price_segment"].value_counts().sort_index()
            fig_seg = px.bar(
                x=seg_counts.index.astype(str),
                y=seg_counts.values,
                title="Products by Price Segment",
                labels={"x": "Segment", "y": "Count"},
                color_discrete_sequence=["#2E86AB"],
            )
            st.plotly_chart(fig_seg, use_container_width=True)

    with tab2:
        rank_by = st.selectbox(
            "Rank brands by",
            [
                "business_performance_score",
                "value_score",
                "total_ratings",
                "avg_rating",
            ],
            format_func=lambda x: x.replace("_", " ").title(),
        )
        top = brand_filtered.nlargest(top_n, rank_by)
        fig_brands = px.bar(
            top.sort_values(rank_by),
            x=rank_by,
            y="brand_name",
            orientation="h",
            title=f"Top {top_n} Brands by {rank_by.replace('_', ' ').title()}",
            labels={rank_by: rank_by.replace("_", " ").title(), "brand_name": "Brand"},
            color_discrete_sequence=["#28A745"],
        )
        st.plotly_chart(fig_brands, use_container_width=True)
        st.dataframe(
            top[
                [
                    "brand_name",
                    "product_count",
                    "avg_price",
                    "avg_rating",
                    "total_ratings",
                    "value_score",
                    "business_performance_score",
                ]
            ].round(2),
            use_container_width=True,
            hide_index=True,
        )

    with tab3:
        segment_stats = (
            filtered.groupby("price_segment", observed=True)
            .agg(
                products=("price", "count"),
                avg_price=("price", "mean"),
                avg_rating=("ratings", "mean"),
                total_ratings=("number_of_ratings", "sum"),
            )
            .reset_index()
        )
        fig_rating = px.scatter(
            segment_stats,
            x="avg_price",
            y="avg_rating",
            size="total_ratings",
            hover_name="price_segment",
            title="Price Segment: Avg Price vs Rating (size = total ratings)",
            labels={"avg_price": "Avg Price (₹)", "avg_rating": "Avg Rating"},
            color_discrete_sequence=["#E62E5C"],
        )
        st.plotly_chart(fig_rating, use_container_width=True)
        st.dataframe(segment_stats.round(2), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
