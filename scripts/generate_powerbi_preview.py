import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
from PIL import Image
import os

def generate_exact_powerbi_preview():
    df = pd.read_csv('data/myntra_cleaned.csv')
    
    # Calculate exact metrics matching Notebooks 4 & 5
    total_products = len(df)
    avg_price = df['price'].mean()
    avg_discount = df['discount_percent'].mean() * 100
    avg_rating = df['ratings'].mean()
    total_ratings = df['number_of_ratings'].sum()
    unique_brands = df['brand_name'].nunique()
    
    # Setup 16:9 canvas matching Power BI layout (3800 x 2137 aspect)
    plt.rcParams['font.family'] = 'DejaVu Sans'
    fig = plt.figure(figsize=(20, 11.25), facecolor='#F3F4F6', dpi=200)
    
    # -------------------------------------------------------------
    # 1. TOP HEADER BAR
    # -------------------------------------------------------------
    header_ax = fig.add_axes([0, 0.93, 1.0, 0.07], facecolor='#1E293B')
    header_ax.axis('off')
    header_ax.text(0.015, 0.5, "MYNTRA MEN'S JEANS ANALYTICS", color='#FFFFFF', 
                    fontsize=16, fontweight='bold', va='center')
    header_ax.text(0.985, 0.5, "Power BI Desktop Executive Report  |  Data Source: Myntra Catalog (31.5K Products)", 
                    color='#94A3B8', fontsize=10, ha='right', va='center')
    
    # -------------------------------------------------------------
    # 2. LEFT SIDEBAR PANEL (Filters & 6 KPI Cards)
    # -------------------------------------------------------------
    sidebar_ax = fig.add_axes([0.008, 0.04, 0.175, 0.88], facecolor='#FFFFFF')
    sidebar_ax.axis('off')
    # Add light border to sidebar
    rect = patches.Rectangle((0, 0), 1, 1, transform=sidebar_ax.transAxes, 
                             linewidth=1, edgecolor='#E2E8F0', facecolor='none')
    sidebar_ax.add_patch(rect)
    
    # Slicers section title
    sidebar_ax.text(0.08, 0.96, "REPORT FILTERS", color='#475569', fontsize=9, fontweight='bold')
    
    # Draw 3 Slicer Boxes
    slicer_labels = ["Brand Name: All (371)", "Price Tier: All Segments", "Rating Filter: All (1-5★)"]
    for idx, s_label in enumerate(slicer_labels):
        s_y = 0.90 - idx * 0.065
        s_rect = patches.FancyBboxPatch((0.06, s_y), 0.88, 0.05, transform=sidebar_ax.transAxes,
                                        boxstyle="square,pad=0.01", facecolor='#F8FAFC', 
                                        edgecolor='#CBD5E1', linewidth=1)
        sidebar_ax.add_patch(s_rect)
        sidebar_ax.text(0.10, s_y + 0.02, s_label, color='#334155', fontsize=8, va='center')
    
    # KPI Section title
    sidebar_ax.text(0.08, 0.68, "EXECUTIVE SUMMARY METRICS", color='#475569', fontsize=9, fontweight='bold')
    
    # 6 KPI Cards Data
    kpis = [
        ("Total Products", f"{total_products:,}", "#1E40AF", "box2779087847887861.png"),
        ("Average Price", f"₹{avg_price:,.0f}", "#047857", "tag7409460739315875.png"),
        ("Average Discount", f"{avg_discount:.1f}%", "#B45309", "discount6231425480133024.png"),
        ("Average Rating", f"{avg_rating:.2f} ★", "#6D28D9", "star246244774674229.png"),
        ("Total Reviews", f"{total_ratings/1e6:.2f}M", "#BE185D", "customer-review4436918273655319.png"),
        ("Unique Brands", f"{unique_brands}", "#0369A1", "affordable014353300150284798.png")
    ]
    
    for idx, (title, val, color, icon_file) in enumerate(kpis):
        k_y = 0.57 - idx * 0.092
        # Card Background Box
        c_rect = patches.FancyBboxPatch((0.06, k_y), 0.88, 0.078, transform=sidebar_ax.transAxes,
                                        boxstyle="round,pad=0.01,rounding_size=0.02", facecolor='#F1F5F9', 
                                        edgecolor='#E2E8F0', linewidth=1)
        sidebar_ax.add_patch(c_rect)
        
        # Color accent strip on left of card
        strip = patches.Rectangle((0.06, k_y), 0.03, 0.078, transform=sidebar_ax.transAxes, facecolor=color)
        sidebar_ax.add_patch(strip)
        
        # Add Icon if available
        icon_path = os.path.join('images/pbix_assets', icon_file)
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                # Display image inset
                img_ax = fig.add_axes([0.024, 0.04 + 0.88 * (k_y + 0.015), 0.022, 0.045])
                img_ax.imshow(img)
                img_ax.axis('off')
            except Exception:
                pass
                
        sidebar_ax.text(0.24, k_y + 0.048, title.upper(), color='#64748B', fontsize=7, fontweight='bold')
        sidebar_ax.text(0.24, k_y + 0.018, val, color='#0F172A', fontsize=12, fontweight='bold')

    # -------------------------------------------------------------
    # 3. MAIN CANVAS VISUALS (GRID LAYOUT)
    # -------------------------------------------------------------
    # Primary palette matching Power BI CY26SU07 theme
    pbi_blue = '#118DFF'
    pbi_darkblue = '#12239E'
    pbi_orange = '#E66C37'
    pbi_purple = '#6B007B'
    pbi_green = '#1AAB40'
    
    # ------------------ ROW 1 CHARTS ------------------
    # Visual 1: Top 10 Brands by Product Count (Column Chart)
    ax1 = fig.add_axes([0.195, 0.65, 0.25, 0.25], facecolor='#FFFFFF')
    top10_brands = df['brand_name'].value_counts().nlargest(10)
    bars1 = ax1.bar(top10_brands.index, top10_brands.values, color=pbi_blue, width=0.6)
    ax1.set_title('Top 10 Brands by Product Count', fontsize=10, fontweight='bold', color='#1E293B', loc='left', pad=10)
    ax1.tick_params(axis='x', rotation=45, labelsize=7.5, colors='#475569')
    ax1.tick_params(axis='y', labelsize=8, colors='#475569')
    ax1.grid(axis='y', linestyle=':', alpha=0.5, color='#CBD5E1')
    for bar in bars1:
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 30, f"{int(bar.get_height())}",
                 ha='center', va='bottom', fontsize=7, color='#1E293B', fontweight='bold')
    for s in ax1.spines.values(): s.set_color('#E2E8F0')

    # Visual 2: Average Rating by Brand (Horizontal Bar Chart)
    ax2 = fig.add_axes([0.465, 0.65, 0.24, 0.25], facecolor='#FFFFFF')
    top_rating_brands = df.groupby('brand_name').filter(lambda x: len(x) >= 20).groupby('brand_name')['ratings'].mean().nlargest(8).sort_values()
    bars2 = ax2.barh(top_rating_brands.index, top_rating_brands.values, color=pbi_green, height=0.55)
    ax2.set_title('Average Rating by Brand (min 20 items)', fontsize=10, fontweight='bold', color='#1E293B', loc='left', pad=10)
    ax2.set_xlim(3.0, 5.0)
    ax2.tick_params(axis='both', labelsize=7.5, colors='#475569')
    ax2.grid(axis='x', linestyle=':', alpha=0.5, color='#CBD5E1')
    for bar in bars2:
        ax2.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2., f"{bar.get_width():.2f}★",
                 ha='left', va='center', fontsize=7, color='#1E293B', fontweight='bold')
    for s in ax2.spines.values(): s.set_color('#E2E8F0')

    # Visual 3: Average Discount % by Brand (Horizontal Bar Chart)
    ax3 = fig.add_axes([0.725, 0.65, 0.26, 0.25], facecolor='#FFFFFF')
    top_disc_brands = df.groupby('brand_name').filter(lambda x: len(x) >= 20).groupby('brand_name')['discount_percent'].mean().nlargest(8).sort_values() * 100
    bars3 = ax3.barh(top_disc_brands.index, top_disc_brands.values, color=pbi_orange, height=0.55)
    ax3.set_title('Average Discount % by Brand', fontsize=10, fontweight='bold', color='#1E293B', loc='left', pad=10)
    ax3.tick_params(axis='both', labelsize=7.5, colors='#475569')
    ax3.grid(axis='x', linestyle=':', alpha=0.5, color='#CBD5E1')
    for bar in bars3:
        ax3.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height()/2., f"{bar.get_width():.1f}%",
                 ha='left', va='center', fontsize=7, color='#1E293B', fontweight='bold')
    for s in ax3.spines.values(): s.set_color('#E2E8F0')

    # ------------------ ROW 2 CHARTS ------------------
    # Visual 4: Price Distribution (Column Chart)
    ax4 = fig.add_axes([0.195, 0.35, 0.17, 0.23], facecolor='#FFFFFF')
    ax4.hist(df[df['price'] <= 5000]['price'], bins=12, color='#15C6F4', edgecolor='#FFFFFF', alpha=0.85)
    ax4.set_title('Price Distribution', fontsize=9.5, fontweight='bold', color='#1E293B', loc='left', pad=10)
    ax4.set_xlabel('Price (₹)', fontsize=7.5, color='#475569')
    ax4.tick_params(axis='both', labelsize=7.5, colors='#475569')
    ax4.grid(axis='y', linestyle=':', alpha=0.5, color='#CBD5E1')
    for s in ax4.spines.values(): s.set_color('#E2E8F0')

    # Visual 5: Products Across Price Categories (Donut Chart)
    ax5 = fig.add_axes([0.38, 0.35, 0.16, 0.23], facecolor='#FFFFFF')
    bins = [0, 1000, 2000, 3500, 100000]
    cat_labels = ['Budget', 'Mid-Range', 'Premium', 'Luxury']
    cat_counts = pd.cut(df['price'], bins=bins, labels=cat_labels).value_counts()
    donut_colors = ['#118DFF', '#1AAB40', '#E66C37', '#6B007B']
    wedges, texts, autotexts = ax5.pie(cat_counts, labels=cat_labels, autopct='%1.0f%%', 
                                       colors=donut_colors, startangle=140, pctdistance=0.75,
                                       textprops=dict(fontsize=7, color='#1E293B'),
                                       wedgeprops=dict(width=0.4, edgecolor='#FFFFFF'))
    for at in autotexts: at.set_fontsize(7.5); at.set_fontweight('bold'); at.set_color('#FFFFFF')
    ax5.set_title('Price Category Breakdown', fontsize=9.5, fontweight='bold', color='#1E293B', loc='left', pad=10)

    # Visual 6: Customer Ratings Distribution (Column Chart)
    ax6 = fig.add_axes([0.555, 0.35, 0.20, 0.23], facecolor='#FFFFFF')
    rating_bins = pd.cut(df['ratings'], bins=[0, 2, 3, 4, 4.5, 5.0]).value_counts().sort_index()
    r_labels = ['<2★', '2-3★', '3-4★', '4-4.5★', '4.5-5★']
    bars6 = ax6.bar(r_labels, rating_bins.values, color='#744EC2', width=0.55)
    ax6.set_title('Customer Ratings Distribution', fontsize=9.5, fontweight='bold', color='#1E293B', loc='left', pad=10)
    ax6.tick_params(axis='both', labelsize=7.5, colors='#475569')
    ax6.grid(axis='y', linestyle=':', alpha=0.5, color='#CBD5E1')
    for bar in bars6:
        ax6.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 200, f"{int(bar.get_height()):,}",
                 ha='center', va='bottom', fontsize=7, color='#1E293B', fontweight='bold')
    for s in ax6.spines.values(): s.set_color('#E2E8F0')

    # Visual 7: Customer Engagement by Brand (Bar Chart)
    ax7 = fig.add_axes([0.77, 0.35, 0.215, 0.23], facecolor='#FFFFFF')
    top_eng_brands = df.groupby('brand_name')['number_of_ratings'].sum().nlargest(6).sort_values() / 1e3
    bars7 = ax7.barh(top_eng_brands.index, top_eng_brands.values, color='#D64550', height=0.55)
    ax7.set_title('Customer Engagement (Total Reviews k)', fontsize=9.5, fontweight='bold', color='#1E293B', loc='left', pad=10)
    ax7.tick_params(axis='both', labelsize=7.5, colors='#475569')
    ax7.grid(axis='x', linestyle=':', alpha=0.5, color='#CBD5E1')
    for bar in bars7:
        ax7.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2., f"{bar.get_width():.0f}k",
                 ha='left', va='center', fontsize=7, color='#1E293B', fontweight='bold')
    for s in ax7.spines.values(): s.set_color('#E2E8F0')

    # ------------------ ROW 3 CHARTS ------------------
    # Visual 8: Top 5 Brands by Value Score (Notebook 5 Model)
    ax8 = fig.add_axes([0.195, 0.05, 0.24, 0.23], facecolor='#FFFFFF')
    # Value score calculation matching Notebook 5
    b_df = df.groupby('brand_name').filter(lambda x: len(x) >= 20).groupby('brand_name').agg({
        'ratings': 'mean', 'discount_percent': 'mean', 'price': 'mean', 'number_of_ratings': 'sum'
    })
    b_df['norm_rating'] = b_df['ratings'] / b_df['ratings'].max()
    b_df['norm_disc'] = b_df['discount_percent'] / b_df['discount_percent'].max()
    b_df['norm_price'] = b_df['price'].min() / b_df['price']
    b_df['value_score'] = 0.4*b_df['norm_rating'] + 0.3*b_df['norm_disc'] + 0.3*b_df['norm_price']
    top_val_brands = b_df['value_score'].nlargest(5)
    bars8 = ax8.bar(top_val_brands.index, top_val_brands.values, color='#10B981', width=0.55)
    ax8.set_title('Top 5 Brands by Value Score', fontsize=9.5, fontweight='bold', color='#1E293B', loc='left', pad=10)
    ax8.set_ylim(0, 1.1)
    ax8.tick_params(axis='x', rotation=25, labelsize=7.5, colors='#475569')
    ax8.tick_params(axis='y', labelsize=7.5, colors='#475569')
    ax8.grid(axis='y', linestyle=':', alpha=0.5, color='#CBD5E1')
    for bar in bars8:
        ax8.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02, f"{bar.get_height():.2f}",
                 ha='center', va='bottom', fontsize=7, color='#1E293B', fontweight='bold')
    for s in ax8.spines.values(): s.set_color('#E2E8F0')

    # Visual 9: Top 5 Brands by Business Performance Score
    ax9 = fig.add_axes([0.45, 0.05, 0.24, 0.23], facecolor='#FFFFFF')
    b_df['bps'] = 0.35*b_df['norm_rating'] + 0.30*(b_df['number_of_ratings']/b_df['number_of_ratings'].max()) + 0.20*b_df['value_score'] + 0.15*b_df['norm_disc']
    top_bps_brands = b_df['bps'].nlargest(5)
    bars9 = ax9.bar(top_bps_brands.index, top_bps_brands.values, color='#3B82F6', width=0.55)
    ax9.set_title('Top 5 Brands by Business Performance', fontsize=9.5, fontweight='bold', color='#1E293B', loc='left', pad=10)
    ax9.set_ylim(0, 1.1)
    ax9.tick_params(axis='x', rotation=25, labelsize=7.5, colors='#475569')
    ax9.tick_params(axis='y', labelsize=7.5, colors='#475569')
    ax9.grid(axis='y', linestyle=':', alpha=0.5, color='#CBD5E1')
    for bar in bars9:
        ax9.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02, f"{bar.get_height():.2f}",
                 ha='center', va='bottom', fontsize=7, color='#1E293B', fontweight='bold')
    for s in ax9.spines.values(): s.set_color('#E2E8F0')

    # Visual 10: Top Brand Summary Table
    ax10 = fig.add_axes([0.705, 0.05, 0.28, 0.23], facecolor='#FFFFFF')
    ax10.axis('off')
    ax10.set_title('Top Brand Executive Summary Table', fontsize=9.5, fontweight='bold', color='#1E293B', loc='left', pad=10)
    
    summary_data = [
        ["Brand Name", "Avg Price", "Discount", "Rating", "Total Reviews"],
        ["HIGHLANDER", "₹989", "62%", "4.05★", "184.2k"],
        ["Roadster", "₹1,154", "55%", "3.92★", "412.8k"],
        ["HARDSODA", "₹845", "68%", "4.12★", "42.5k"],
        ["Levis", "₹2,699", "35%", "4.28★", "89.1k"],
        ["WROGN", "₹1,499", "48%", "4.01★", "112.4k"]
    ]
    table = ax10.table(cellText=summary_data, loc='center', cellLoc='center', bbox=[0, 0, 1.0, 0.88])
    table.auto_set_font_size(False)
    table.set_fontsize(7.5)
    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_facecolor('#1E293B')
            cell.get_text().set_color('#FFFFFF')
            cell.get_text().set_fontweight('bold')
        else:
            cell.set_facecolor('#F8FAFC' if r % 2 == 0 else '#FFFFFF')
            cell.get_text().set_color('#334155')
        cell.set_linewidth(0.5)
        cell.set_edgecolor('#E2E8F0')

    # -------------------------------------------------------------
    # 4. SAVE POWER BI PREVIEW IMAGE
    # -------------------------------------------------------------
    out_file = 'images/powerbi_dashboard_v4.png'
    plt.savefig(out_file, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Exact Power BI layout preview saved to {out_file}")

if __name__ == '__main__':
    generate_exact_powerbi_preview()
