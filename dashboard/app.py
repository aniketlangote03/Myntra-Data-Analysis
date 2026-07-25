"""Interactive Streamlit dashboard for Myntra Men's Jeans analysis."""

import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "myntra_cleaned.csv"

PRICE_BINS = [0, 500, 1000, 2000, 5000, float("inf")]
PRICE_LABELS = ["≤₹500", "₹501–1000", "₹1001–2000", "₹2001–5000", ">₹5000"]
COLOR_PALETTE = ["#E62E5C", "#2E86AB", "#28A745", "#F18F01", "#7209B7", "#4CC9F0"]


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error(
            f"❌ **Dataset not found at `{DATA_PATH}`.**\n\n"
            "Please run **Notebook 03 (Data Cleaning)** first to generate `data/myntra_cleaned.csv`."
        )
        st.stop()
    df = pd.read_csv(DATA_PATH)
    df["price_segment"] = pd.cut(df["price"], bins=PRICE_BINS, labels=PRICE_LABELS)
    df["discount_display"] = df["discount_percent"] * 100
    df["fit_type"] = (
        df["pants_description"]
        .str.extract(
            r"(Slim|Relaxed|Straight|Baggy|Bootcut|Skinny|Loose|Tapered|Cargo|Jogger|Flared)",
            flags=re.IGNORECASE,
            expand=False,
        )
        .str.title()
        .fillna("Regular/Other")
    )
    return df


def calculate_brand_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    brand = (
        df.groupby("brand_name")
        .agg(
            product_count=("price", "count"),
            avg_price=("price", "mean"),
            avg_mrp=("MRP", "mean"),
            avg_discount=("discount_display", "mean"),
            avg_rating=("ratings", "mean"),
            total_ratings=("number_of_ratings", "sum"),
        )
        .reset_index()
    )

    brand["ratings_per_product"] = brand["total_ratings"] / brand["product_count"]

    # Score components (safe division against max/min)
    max_rating = brand["avg_rating"].max() if brand["avg_rating"].max() > 0 else 1
    max_discount = brand["avg_discount"].max() if brand["avg_discount"].max() > 0 else 1
    min_price = brand["avg_price"].min() if brand["avg_price"].min() > 0 else 1

    brand["rating_score"] = brand["avg_rating"] / max_rating
    brand["discount_score"] = brand["avg_discount"] / max_discount
    brand["price_score"] = min_price / brand["avg_price"].clip(lower=1)
    brand["value_score"] = (
        0.40 * brand["rating_score"]
        + 0.30 * brand["discount_score"]
        + 0.30 * brand["price_score"]
    )

    # Normalize metrics for performance score
    for col in ["avg_rating", "ratings_per_product", "value_score", "avg_discount"]:
        c_min = brand[col].min()
        c_max = brand[col].max()
        denom = (c_max - c_min) if (c_max - c_min) > 0 else 1
        brand[f"{col}_norm"] = (brand[col] - c_min) / denom

    brand["business_performance_score"] = (
        0.35 * brand["avg_rating_norm"]
        + 0.30 * brand["ratings_per_product_norm"]
        + 0.20 * brand["value_score_norm"]
        + 0.15 * brand["avg_discount_norm"]
    )
    return brand.sort_values("business_performance_score", ascending=False)


def generate_insights(filtered: pd.DataFrame, brands: pd.DataFrame) -> list[str]:
    insights = []
    if filtered.empty or brands.empty:
        return ["No products fit current filter selection."]

    # 1. Price Sweet Spot
    mode_segment = filtered["price_segment"].mode()
    if not mode_segment.empty:
        seg_name = mode_segment[0]
        seg_pct = (filtered["price_segment"] == seg_name).mean() * 100
        insights.append(
            f"🎯 <b>Assortment Density</b>: The <b>{seg_name}</b> segment dominates with <b>{seg_pct:.1f}%</b> of all active products."
        )

    # 2. Top Performing Brand
    top_brand = brands.iloc[0]
    insights.append(
        f"🏆 <b>Top Brand Score</b>: <b>{top_brand['brand_name']}</b> achieves the highest Business Score (<b>{top_brand['business_performance_score']:.2f}</b>) with an avg rating of <b>{top_brand['avg_rating']:.2f}★</b>."
    )

    # 3. Rating vs Discount Correlation
    corr = filtered["ratings"].corr(filtered["discount_display"])
    if not pd.isna(corr):
        direction = "positive" if corr > 0.05 else ("negative" if corr < -0.05 else "neutral")
        insights.append(
            f"📈 <b>Discount Impact</b>: Weak {direction} correlation (<b>{corr:.2f}</b>) between discount % and rating—high discounts do not compromise perceived product quality."
        )

    # 4. Most Popular Fit
    top_fit = filtered["fit_type"].value_counts().index[0]
    insights.append(
        f"✂️ <b>Most Popular Cut</b>: <b>{top_fit}</b> is the most frequent fit cut in this selection."
    )

    return insights


def apply_custom_css() -> None:
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #E62E5C;
            margin-bottom: 0px;
        }
        .sub-header {
            font-size: 1.0rem;
            color: #6C757D;
            margin-bottom: 15px;
        }
        .insight-box {
            background: linear-gradient(135deg, rgba(230, 46, 92, 0.08), rgba(46, 134, 171, 0.08));
            border-left: 4px solid #E62E5C;
            border-radius: 8px;
            padding: 14px 20px;
            margin-bottom: 20px;
        }
        .metric-card {
            background-color: rgba(230, 46, 92, 0.05);
            border-left: 4px solid #E62E5C;
            border-radius: 8px;
            padding: 12px 18px;
            margin-bottom: 15px;
        }
        .metric-label {
            font-size: 0.85rem;
            color: #6C757D;
            font-weight: 600;
            text-transform: uppercase;
        }
        .metric-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #1E293B;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Myntra Men's Jeans Analytics",
        page_icon="👖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_custom_css()

    df = load_data()

    # Header
    st.markdown('<div class="main-header">👖 Myntra Men\'s Jeans Analytics</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub-header">Analyzing <b>{len(df):,}</b> products across <b>{df["brand_name"].nunique()}</b> brands • Interactive market positioning & performance explorer</div>',
        unsafe_allow_html=True,
    )

    # Sidebar Filters
    with st.sidebar:
        st.header("⚡ Global Filters")

        selected_segments = st.multiselect(
            "Price Segment",
            options=PRICE_LABELS,
            default=list(PRICE_LABELS),
            help="Filter analysis by target price range",
        )

        all_fits = sorted(df["fit_type"].unique().tolist())
        selected_fits = st.multiselect(
            "Fit Type",
            options=all_fits,
            default=all_fits,
            help="Filter by jeans cut style",
        )

        min_products = st.slider(
            "Min Products per Brand",
            min_value=1,
            max_value=50,
            value=10,
            help="Filters out niche/low-sample brands from brand rankings",
        )

        top_n = st.slider(
            "Top N Brands to Display",
            min_value=5,
            max_value=30,
            value=10,
        )

        search_query = st.text_input("🔍 Search Brand or Style", "", help="Filter by product name or brand")

    # Apply Filters
    filtered = df[
        (df["price_segment"].isin(selected_segments)) & (df["fit_type"].isin(selected_fits))
    ]

    if search_query:
        filtered = filtered[
            filtered["brand_name"].str.contains(search_query, case=False, na=False)
            | filtered["pants_description"].str.contains(search_query, case=False, na=False)
        ]

    # Dynamically re-calculate brand metrics on active filtered data
    brands = calculate_brand_metrics(filtered)
    brand_filtered = brands[brands["product_count"] >= min_products] if not brands.empty else pd.DataFrame()

    # Executive Insights Box
    if not filtered.empty and not brands.empty:
        insights = generate_insights(filtered, brands)
        with st.expander("💡 **Dynamic Market Insights (Click to toggle)**", expanded=True):
            st.markdown(
                '<div class="insight-box">'
                + "".join([f"<p style='margin-bottom:6px;'>{ins}</p>" for ins in insights])
                + "</div>",
                unsafe_allow_html=True,
            )

    # Dynamic KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Products</div><div class="metric-value">{len(filtered):,}</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        avg_p = filtered["price"].mean() if not filtered.empty else 0
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Avg Selling Price</div><div class="metric-value">₹{avg_p:,.0f}</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        avg_disc = filtered["discount_display"].mean() if not filtered.empty else 0
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Avg Discount</div><div class="metric-value">{avg_disc:.0f}%</div></div>',
            unsafe_allow_html=True,
        )
    with col4:
        avg_r = filtered["ratings"].mean() if not filtered.empty else 0
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Avg Rating</div><div class="metric-value">{avg_r:.2f} ★</div></div>',
            unsafe_allow_html=True,
        )
    with col5:
        tot_rev = filtered["number_of_ratings"].sum() if not filtered.empty else 0
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Total Reviews</div><div class="metric-value">{tot_rev:,.0f}</div></div>',
            unsafe_allow_html=True,
        )

    if filtered.empty:
        st.warning("⚠️ No products match your filter criteria. Please adjust your sidebar settings.")
        return

    # Navigation Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Overview & Price",
            "🏆 Brand Rankings",
            "⚔️ Brand Duel (Comparison)",
            "✂️ Fit & Segment Insights",
            "🔍 Product Explorer",
        ]
    )

    # TAB 1: OVERVIEW & PRICE DISTRIBUTION
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            fig_price = px.histogram(
                filtered,
                x="price",
                nbins=50,
                title="Selling Price Distribution (₹)",
                labels={"price": "Price (₹)", "count": "Product Count"},
                color_discrete_sequence=["#E62E5C"],
                marginal="box",
            )
            fig_price.update_layout(hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_price, use_container_width=True)

        with c2:
            seg_counts = filtered["price_segment"].value_counts().reindex(PRICE_LABELS).fillna(0)
            fig_seg = px.bar(
                x=seg_counts.index.astype(str),
                y=seg_counts.values,
                title="Product Density by Price Segment",
                labels={"x": "Price Segment", "y": "Product Count"},
                color=seg_counts.values,
                color_continuous_scale="Reds",
            )
            fig_seg.update_layout(coloraxis_showscale=False, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_seg, use_container_width=True)

        st.subheader("Price vs. Discount Matrix")
        fig_scatter = px.scatter(
            filtered,
            x="price",
            y="discount_display",
            color="ratings",
            size="number_of_ratings",
            hover_name="pants_description",
            hover_data=["brand_name", "MRP", "price"],
            title="Price vs. Discount % (Color = Rating, Size = Rating Volume)",
            labels={"price": "Selling Price (₹)", "discount_display": "Discount (%)", "ratings": "Rating"},
            color_continuous_scale="Viridis",
            opacity=0.7,
        )
        fig_scatter.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_scatter, use_container_width=True)

    # TAB 2: BRAND RANKINGS
    with tab2:
        if brand_filtered.empty:
            st.warning(f"No brands meet the threshold of ≥ {min_products} products under current filters.")
        else:
            rank_col1, rank_col2 = st.columns([1, 2])
            with rank_col1:
                rank_by = st.selectbox(
                    "Rank Brands By",
                    [
                        "business_performance_score",
                        "value_score",
                        "total_ratings",
                        "avg_rating",
                        "avg_discount",
                        "avg_price",
                        "product_count",
                    ],
                    format_func=lambda x: x.replace("_", " ").title(),
                )

            top = brand_filtered.nlargest(top_n, rank_by)

            fig_brands = px.bar(
                top.sort_values(rank_by),
                x=rank_by,
                y="brand_name",
                orientation="h",
                title=f"Top {len(top)} Brands by {rank_by.replace('_', ' ').title()}",
                labels={rank_by: rank_by.replace("_", " ").title(), "brand_name": "Brand"},
                color=rank_by,
                color_continuous_scale="Tealgrn",
            )
            fig_brands.update_layout(coloraxis_showscale=False, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_brands, use_container_width=True)

            st.subheader("📋 Brand Performance Leaderboard")
            display_df = top[
                [
                    "brand_name",
                    "product_count",
                    "avg_price",
                    "avg_discount",
                    "avg_rating",
                    "total_ratings",
                    "value_score",
                    "business_performance_score",
                ]
            ].copy()

            display_df = display_df.rename(
                columns={
                    "brand_name": "Brand",
                    "product_count": "Products",
                    "avg_price": "Avg Price (₹)",
                    "avg_discount": "Avg Discount (%)",
                    "avg_rating": "Avg Rating",
                    "total_ratings": "Total Reviews",
                    "value_score": "Value Score",
                    "business_performance_score": "Business Score",
                }
            )

            st.dataframe(
                display_df.round(2).style.background_gradient(subset=["Business Score", "Avg Rating"], cmap="Reds"),
                use_container_width=True,
                hide_index=True,
            )

    # TAB 3: BRAND DUEL (SIDE-BY-SIDE COMPARISON)
    with tab3:
        st.subheader("⚔️ Head-to-Head Brand Comparison")
        all_brands_list = sorted(filtered["brand_name"].unique().tolist())
        if len(all_brands_list) < 2:
            st.info("At least 2 brands are required in current filter view for head-to-head comparison.")
        else:
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                brand1 = st.selectbox("Select Brand 1", options=all_brands_list, index=0)
            with b_col2:
                default_idx = 1 if len(all_brands_list) > 1 else 0
                brand2 = st.selectbox("Select Brand 2", options=all_brands_list, index=default_idx)

            if brand1 == brand2:
                st.warning("Please select two different brands to compare.")
            else:
                df_b1 = filtered[filtered["brand_name"] == brand1]
                df_b2 = filtered[filtered["brand_name"] == brand2]

                m1_col, m2_col = st.columns(2)
                with m1_col:
                    st.markdown(f"### **{brand1}**")
                    st.write(f"• **Products**: {len(df_b1):,}")
                    st.write(f"• **Avg Price**: ₹{df_b1['price'].mean():,.0f}")
                    st.write(f"• **Avg Discount**: {df_b1['discount_display'].mean():.1f}%")
                    st.write(f"• **Avg Rating**: {df_b1['ratings'].mean():.2f} ★")
                    st.write(f"• **Total Reviews**: {df_b1['number_of_ratings'].sum():,.0f}")

                with m2_col:
                    st.markdown(f"### **{brand2}**")
                    st.write(f"• **Products**: {len(df_b2):,}")
                    st.write(f"• **Avg Price**: ₹{df_b2['price'].mean():,.0f}")
                    st.write(f"• **Avg Discount**: {df_b2['discount_display'].mean():.1f}%")
                    st.write(f"• **Avg Rating**: {df_b2['ratings'].mean():.2f} ★")
                    st.write(f"• **Total Reviews**: {df_b2['number_of_ratings'].sum():,.0f}")

                # Overlay Histogram of Price
                combined_b = filtered[filtered["brand_name"].isin([brand1, brand2])]
                fig_comp_price = px.histogram(
                    combined_b,
                    x="price",
                    color="brand_name",
                    barmode="overlay",
                    title=f"Price Distribution Comparison: {brand1} vs {brand2}",
                    labels={"price": "Selling Price (₹)", "brand_name": "Brand"},
                    color_discrete_sequence=["#E62E5C", "#2E86AB"],
                    opacity=0.6,
                )
                st.plotly_chart(fig_comp_price, use_container_width=True)

    # TAB 4: FIT & SEGMENT INSIGHTS
    with tab4:
        fc1, fc2 = st.columns(2)
        with fc1:
            fit_stats = (
                filtered.groupby("fit_type")
                .agg(
                    products=("price", "count"),
                    avg_price=("price", "mean"),
                    avg_rating=("ratings", "mean"),
                    avg_discount=("discount_display", "mean"),
                )
                .reset_index()
                .sort_values("products", ascending=False)
            )

            fig_fit = px.bar(
                fit_stats,
                x="fit_type",
                y="products",
                color="avg_rating",
                title="Product Availability & Rating by Fit Cut",
                labels={"fit_type": "Fit Cut", "products": "Product Count", "avg_rating": "Avg Rating"},
                color_continuous_scale="Plasma",
            )
            st.plotly_chart(fig_fit, use_container_width=True)

        with fc2:
            fig_box = px.box(
                filtered,
                x="price_segment",
                y="ratings",
                color="price_segment",
                title="Rating Distribution Across Price Segments",
                labels={"price_segment": "Price Segment", "ratings": "Rating (★)"},
                color_discrete_sequence=COLOR_PALETTE,
            )
            fig_box.update_layout(showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)

        st.subheader("Price Segment Benchmark Summary")
        segment_stats = (
            filtered.groupby("price_segment", observed=True)
            .agg(
                Products=("price", "count"),
                Avg_Price=("price", "mean"),
                Avg_Discount=("discount_display", "mean"),
                Avg_Rating=("ratings", "mean"),
                Total_Reviews=("number_of_ratings", "sum"),
            )
            .reset_index()
        )
        segment_stats.columns = [
            "Price Segment",
            "Products",
            "Avg Price (₹)",
            "Avg Discount (%)",
            "Avg Rating",
            "Total Reviews",
        ]
        st.dataframe(segment_stats.round(2), use_container_width=True, hide_index=True)

    # TAB 5: PRODUCT EXPLORER
    with tab5:
        st.subheader("🔍 Detailed Product Catalog Search")
        search_cols = [
            "brand_name",
            "pants_description",
            "fit_type",
            "price_segment",
            "price",
            "MRP",
            "discount_display",
            "ratings",
            "number_of_ratings",
        ]

        catalog = filtered[search_cols].copy()
        catalog.columns = [
            "Brand",
            "Description",
            "Fit Style",
            "Price Segment",
            "Price (₹)",
            "MRP (₹)",
            "Discount (%)",
            "Rating ★",
            "Review Count",
        ]

        st.dataframe(
            catalog.sort_values("Rating ★", ascending=False).round(2),
            use_container_width=True,
            hide_index=True,
        )

        # Download CSV option
        csv_data = catalog.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Filtered Catalog as CSV",
            data=csv_data,
            file_name="myntra_jeans_filtered_export.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
