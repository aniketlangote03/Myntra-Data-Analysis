import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_powerbi_preview():
    # Load dataset
    df = pd.read_csv('data/myntra_cleaned.csv')
    
    # Set dark executive theme matching Power BI
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 9), facecolor='#111827')
    
    # Title Header Bar
    fig.text(0.03, 0.94, 'Power BI Analytics | Myntra Men\'s Jeans Executive Report', 
             fontsize=20, fontweight='bold', color='#F3F4F6')
    fig.text(0.03, 0.91, 'Source: PowerBi/Myntra Sales Analytics.pbix  •  Cleaned Catalog: 31,527 Products  •  371 Brands', 
             fontsize=11, color='#9CA3AF')
    
    # -------------------------------------------------------------
    # Top KPI Cards (4 KPI Metric Boxes)
    # -------------------------------------------------------------
    kpis = [
        ("TOTAL PRODUCTS", f"{len(df):,}", "31,527 Verified Items", "#F59E0B"),
        ("AVG SELLING PRICE", f"₹{df['price'].mean():,.0f}", "Median: ₹1,484", "#10B981"),
        ("AVG DISCOUNT", f"{df['discount_percent'].mean()*100:.1f}%", "Max: 90%", "#3B82F6"),
        ("TOTAL REVIEWS", f"{df['number_of_ratings'].sum()/1e6:.2f}M", "Avg Rating: 3.98★", "#EC4899")
    ]
    
    for i, (title, value, subtext, color) in enumerate(kpis):
        left = 0.03 + i * 0.2375
        ax_kpi = fig.add_axes([left, 0.77, 0.22, 0.11], facecolor='#1F2937')
        ax_kpi.set_xticks([])
        ax_kpi.set_yticks([])
        for spine in ax_kpi.spines.values():
            spine.set_color(color)
            spine.set_linewidth(1.5)
            
        ax_kpi.text(0.08, 0.72, title, fontsize=9, fontweight='bold', color=color)
        ax_kpi.text(0.08, 0.36, value, fontsize=18, fontweight='bold', color='#FFFFFF')
        ax_kpi.text(0.08, 0.12, subtext, fontsize=8, color='#9CA3AF')

    # -------------------------------------------------------------
    # Visual 1: Price Segment Breakdown (Top-Left Plot)
    # -------------------------------------------------------------
    ax1 = fig.add_axes([0.03, 0.42, 0.44, 0.28], facecolor='#1F2937')
    bins = [0, 1000, 2000, 3500, 100000]
    labels = ['Budget (<₹1k)', 'Mid-Range (₹1-2k)', 'Premium (₹2-3.5k)', 'Luxury (>₹3.5k)']
    df['segment'] = pd.cut(df['price'], bins=bins, labels=labels)
    segment_counts = df['segment'].value_counts().reindex(labels)
    
    colors1 = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444']
    bars = ax1.bar(segment_counts.index, segment_counts.values, color=colors1, width=0.55, edgecolor='none')
    ax1.set_title('Product Catalog Volume by Price Segment', fontsize=12, fontweight='bold', color='#F3F4F6', pad=10)
    ax1.tick_params(colors='#D1D5DB', labelsize=9)
    ax1.grid(axis='y', linestyle='--', alpha=0.2, color='#9CA3AF')
    for spine in ax1.spines.values():
        spine.set_visible(False)
        
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 300, f"{int(height):,}",
                 ha='center', va='bottom', fontsize=9, color='#FFFFFF', fontweight='bold')

    # -------------------------------------------------------------
    # Visual 2: Top Brands by Customer Reviews (Top-Right Plot)
    # -------------------------------------------------------------
    ax2 = fig.add_axes([0.53, 0.42, 0.44, 0.28], facecolor='#1F2937')
    top_brands = df.groupby('brand_name')['number_of_ratings'].sum().nlargest(8).sort_values(ascending=True)
    bars2 = ax2.barh(top_brands.index, top_brands.values / 1e3, color='#F59E0B', height=0.55)
    ax2.set_title('Top 8 Brands by Total Reviews (in Thousands)', fontsize=12, fontweight='bold', color='#F3F4F6', pad=10)
    ax2.tick_params(colors='#D1D5DB', labelsize=9)
    ax2.grid(axis='x', linestyle='--', alpha=0.2, color='#9CA3AF')
    for spine in ax2.spines.values():
        spine.set_visible(False)
        
    for bar in bars2:
        width = bar.get_width()
        ax2.text(width + 5, bar.get_y() + bar.get_height()/2., f"{width:.0f}k",
                 ha='left', va='center', fontsize=9, color='#FFFFFF', fontweight='bold')

    # -------------------------------------------------------------
    # Visual 3: Price vs Rating Scatter & Density (Bottom-Left)
    # -------------------------------------------------------------
    ax3 = fig.add_axes([0.03, 0.07, 0.44, 0.28], facecolor='#1F2937')
    sample_df = df.sample(min(2000, len(df)), random_state=42)
    sc = ax3.scatter(sample_df['price'], sample_df['ratings'], c=sample_df['discount_percent']*100,
                    cmap='viridis', alpha=0.6, s=18, edgecolors='none')
    ax3.set_title('Price vs Customer Rating (Color: Discount %)', fontsize=12, fontweight='bold', color='#F3F4F6', pad=10)
    ax3.set_xlabel('Selling Price (₹)', color='#9CA3AF', fontsize=9)
    ax3.set_ylabel('Customer Rating (1-5★)', color='#9CA3AF', fontsize=9)
    ax3.set_xlim(0, 7000)
    ax3.tick_params(colors='#D1D5DB', labelsize=9)
    ax3.grid(True, linestyle='--', alpha=0.15, color='#9CA3AF')
    for spine in ax3.spines.values():
        spine.set_visible(False)
    cbar = plt.colorbar(sc, ax=ax3, fraction=0.03, pad=0.02)
    cbar.ax.tick_params(labelsize=8, colors='#D1D5DB')
    cbar.set_label('Discount %', color='#9CA3AF', fontsize=8)

    # -------------------------------------------------------------
    # Visual 4: Discount Distribution Across Brands (Bottom-Right)
    # -------------------------------------------------------------
    ax4 = fig.add_axes([0.53, 0.07, 0.44, 0.28], facecolor='#1F2937')
    top_vol_brands = df['brand_name'].value_counts().nlargest(6).index
    df_top_vol = df[df['brand_name'].isin(top_vol_brands)]
    sns.boxplot(data=df_top_vol, x='brand_name', y='discount_percent', ax=ax4, palette='mako', width=0.45)
    ax4.set_title('Discount Spread for Top Volume Brands', fontsize=12, fontweight='bold', color='#F3F4F6', pad=10)
    ax4.set_xlabel('', color='#9CA3AF')
    ax4.set_ylabel('Discount Decimal (0.0 - 1.0)', color='#9CA3AF', fontsize=9)
    ax4.tick_params(colors='#D1D5DB', labelsize=8)
    ax4.grid(axis='y', linestyle='--', alpha=0.15, color='#9CA3AF')
    for spine in ax4.spines.values():
        spine.set_visible(False)

    # Save output image
    os.makedirs('images', exist_ok=True)
    out_path = 'images/powerbi_dashboard.png'
    plt.savefig(out_path, dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f"Power BI dashboard preview successfully saved to {out_path}")

if __name__ == '__main__':
    generate_powerbi_preview()
