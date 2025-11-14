"""
Executive-Ready Customer Spending Analysis Dashboard
Modern, minimalist design with clear visual hierarchy
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Rectangle, FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

# Modern color palette - harmonious and distinct
COLORS = {
    'premium': '#C41E3A',        # Rich burgundy
    'luxury': '#FF6B6B',         # Coral red
    'standard': '#4ECDC4',       # Teal
    'background': '#F8F9FA',     # Soft gray
    'accent': '#2C3E50',          # Dark slate
    'text': '#34495E',           # Charcoal
    'light_bg': '#FFFFFF',       # White
    'border': '#E0E0E0',         # Light gray border
    'electronics': '#6C5CE7',    # Purple
    'home_kitchen': '#00B894',   # Green
    'accessories': '#FDCB6E',    # Yellow
    'sports': '#E17055',         # Orange
    'other': '#74B9FF'           # Blue
}

# Set modern style
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']

def load_data(db_path="ecommerce.db"):
    """Load customer spending data by product categories."""
    conn = sqlite3.connect(db_path)
    
    query = """
    WITH CategorySpending AS (
        SELECT 
            p.category,
            p.price,
            oi.subtotal AS item_revenue,
            o.order_id,
            o.customer_id,
            oi.quantity,
            CASE 
                WHEN p.price >= 500 THEN 'Premium'
                WHEN p.price >= 200 THEN 'Luxury'
                ELSE 'Standard'
            END AS price_tier
        FROM Orders o
        JOIN Order_Items oi ON o.order_id = oi.order_id
        JOIN Products p ON oi.product_id = p.product_id
    )
    SELECT 
        category,
        price_tier,
        SUM(item_revenue) AS total_revenue,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS unique_customers,
        SUM(quantity) AS total_items_sold,
        AVG(price) AS avg_price
    FROM CategorySpending
    GROUP BY category, price_tier
    ORDER BY total_revenue DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def create_metric_card(ax, value, label, color):
    """Create a styled metric card with perfect alignment."""
    ax.axis('off')
    
    # Add shadow effect
    shadow = FancyBboxPatch((0.015, -0.015), 1, 1,
                           boxstyle="round,pad=0.02",
                           facecolor='black',
                           alpha=0.12,
                           transform=ax.transAxes,
                           zorder=0)
    ax.add_patch(shadow)
    
    # Create rounded rectangle background - perfectly centered
    fancy_box = FancyBboxPatch((0, 0), 1, 1,
                              boxstyle="round,pad=0.025",
                              facecolor=color,
                              edgecolor='white',
                              linewidth=2.5,
                              transform=ax.transAxes,
                              zorder=1)
    ax.add_patch(fancy_box)
    
    # Add text - perfectly centered
    ax.text(0.5, 0.62, value, ha='center', va='center',
           fontsize=26, fontweight='bold', color='white',
           transform=ax.transAxes, zorder=2)
    ax.text(0.5, 0.28, label, ha='center', va='center',
           fontsize=12, color='white', weight='normal',
           transform=ax.transAxes, zorder=2)

def create_executive_summary_box(ax, df, premium_luxury, category_totals):
    """Create a clean executive summary box with perfect alignment."""
    ax.axis('off')
    
    total_revenue = df['total_revenue'].sum()
    premium_luxury_revenue = premium_luxury['total_revenue'].sum() if len(premium_luxury) > 0 else 0
    premium_luxury_pct = (premium_luxury_revenue / total_revenue * 100) if total_revenue > 0 else 0
    top_category = category_totals.index[0]
    top_category_revenue = category_totals.iloc[0]
    avg_order_value = df['total_revenue'].sum() / df['total_orders'].sum() if df['total_orders'].sum() > 0 else 0
    
    # Create semi-transparent background with shadow
    shadow = FancyBboxPatch((0.01, -0.01), 1, 1,
                           boxstyle="round,pad=0.03",
                           facecolor='black',
                           alpha=0.05,
                           transform=ax.transAxes,
                           zorder=0)
    ax.add_patch(shadow)
    
    fancy_box = FancyBboxPatch((0, 0), 1, 1,
                              boxstyle="round,pad=0.04",
                              facecolor='white',
                              edgecolor=COLORS['accent'],
                              linewidth=2.5,
                              alpha=0.95,
                              transform=ax.transAxes,
                              zorder=1)
    ax.add_patch(fancy_box)
    
    # Title - centered and aligned
    ax.text(0.5, 0.90, 'EXECUTIVE SUMMARY', ha='center', va='top',
           fontsize=17, fontweight='bold', color=COLORS['accent'],
           transform=ax.transAxes, zorder=2)
    
    # Divider line
    ax.plot([0.1, 0.9], [0.82, 0.82], color=COLORS['border'], 
           linewidth=1.5, transform=ax.transAxes, zorder=2)
    
    # Key metrics - left-aligned with consistent spacing
    y_pos = 0.70
    metrics = [
        f"Total Revenue: ${total_revenue:,.0f}",
        f"Premium/Luxury: {premium_luxury_pct:.1f}% of revenue",
        f"Top Category: {top_category}",
        f"Avg Order Value: ${avg_order_value:,.0f}"
    ]
    
    for metric in metrics:
        ax.text(0.10, y_pos, f"• {metric}", ha='left', va='top',
               fontsize=11.5, color=COLORS['text'],
               transform=ax.transAxes, zorder=2)
        y_pos -= 0.14

def create_category_revenue_chart(ax, df, category_totals):
    """Create main revenue chart with modern styling."""
    categories = category_totals.index
    x_pos = np.arange(len(categories))
    width = 0.65
    
    # Prepare stacked data
    premium_data = []
    luxury_data = []
    standard_data = []
    
    for cat in categories:
        cat_df = df[df['category'] == cat]
        premium_data.append(cat_df[cat_df['price_tier'] == 'Premium']['total_revenue'].sum())
        luxury_data.append(cat_df[cat_df['price_tier'] == 'Luxury']['total_revenue'].sum())
        standard_data.append(cat_df[cat_df['price_tier'] == 'Standard']['total_revenue'].sum())
    
    premium_data = np.array(premium_data)
    luxury_data = np.array(luxury_data)
    standard_data = np.array(standard_data)
    
    # Create stacked bars with increased thickness
    bars1 = ax.bar(x_pos, standard_data, width, label='Standard', 
                   color=COLORS['standard'], alpha=0.85, edgecolor='white', linewidth=2)
    bars2 = ax.bar(x_pos, luxury_data, width, bottom=standard_data, label='Luxury', 
                   color=COLORS['luxury'], alpha=0.85, edgecolor='white', linewidth=2)
    bars3 = ax.bar(x_pos, premium_data, width, bottom=standard_data + luxury_data, 
                   label='Premium', color=COLORS['premium'], alpha=0.85, 
                   edgecolor='white', linewidth=2)
    
    # Styling
    ax.set_xlabel('Product Category', fontsize=13, fontweight='bold', color=COLORS['text'], labelpad=15)
    ax.set_ylabel('Revenue ($)', fontsize=13, fontweight='bold', color=COLORS['text'], labelpad=15)
    ax.set_title('Revenue by Category', fontsize=15, fontweight='bold', 
                 color=COLORS['accent'], pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, fontsize=11, color=COLORS['text'])
    ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True,
             fontsize=10, framealpha=0.9)
    ax.grid(axis='y', alpha=0.2, linestyle='--', linewidth=0.8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLORS['border'])
    ax.spines['bottom'].set_color(COLORS['border'])
    
    # Add value labels only on highest bars
    total_heights = standard_data + luxury_data + premium_data
    max_height = total_heights.max()
    threshold = max_height * 0.15  # Only label bars above 15% of max
    
    for i, (bar, height) in enumerate(zip(bars3, total_heights)):
        if height > threshold:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:,.0f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold',
                   color=COLORS['text'])

def create_tier_comparison_chart(ax, df):
    """Create modern donut chart."""
    tier_totals = df.groupby('price_tier')['total_revenue'].sum()
    
    labels = ['Standard', 'Luxury', 'Premium']
    colors_list = [COLORS['standard'], COLORS['luxury'], COLORS['premium']]
    sizes = [tier_totals.get('Standard', 0), 
             tier_totals.get('Luxury', 0), 
             tier_totals.get('Premium', 0)]
    
    # Create donut chart
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_list,
                                      autopct='%1.1f%%', startangle=90,
                                      pctdistance=0.85, labeldistance=1.1,
                                      textprops={'fontsize': 11, 'fontweight': 'bold',
                                                'color': COLORS['text']},
                                      wedgeprops={'edgecolor': 'white', 'linewidth': 3})
    
    # Draw center circle
    centre_circle = plt.Circle((0,0), 0.65, fc='white', edgecolor=COLORS['border'], linewidth=2)
    ax.add_artist(centre_circle)
    
    # Add total in center
    total = sum(sizes)
    ax.text(0, 0, f'${total:,.0f}\nTotal', ha='center', va='center',
           fontsize=14, fontweight='bold', color=COLORS['accent'])
    
    ax.set_title('Revenue Distribution', fontsize=14, fontweight='bold',
                color=COLORS['accent'], pad=20)
    
    # Style autopct
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)

def create_customer_distribution_chart(ax, df):
    """Create horizontal bar chart with modern styling."""
    customer_by_category = df.groupby('category')['unique_customers'].sum().sort_values(ascending=True)
    
    # Map categories to colors
    category_colors = {
        'Electronics': COLORS['electronics'],
        'Home & Kitchen': COLORS['home_kitchen'],
        'Accessories': COLORS['accessories'],
        'Sports & Outdoors': COLORS['sports']
    }
    
    colors_map = [category_colors.get(cat, COLORS['other']) for cat in customer_by_category.index]
    
    bars = ax.barh(range(len(customer_by_category)), customer_by_category.values,
                   color=colors_map, alpha=0.85, edgecolor='white', linewidth=2, height=0.6)
    
    ax.set_yticks(range(len(customer_by_category)))
    ax.set_yticklabels(customer_by_category.index, fontsize=11, color=COLORS['text'])
    ax.set_xlabel('Unique Customers', fontsize=12, fontweight='bold', color=COLORS['text'], labelpad=12)
    ax.set_title('Customer Reach by Category', fontsize=14, fontweight='bold',
                color=COLORS['accent'], pad=20)
    ax.grid(axis='x', alpha=0.2, linestyle='--', linewidth=0.8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLORS['border'])
    ax.spines['bottom'].set_color(COLORS['border'])
    
    # Add value labels
    for bar, val in zip(bars, customer_by_category.values):
        ax.text(val + 1, bar.get_y() + bar.get_height()/2, f'{int(val)}',
               ha='left', va='center', fontsize=11, fontweight='bold', color=COLORS['text'])

def create_avg_order_value_chart(ax, df):
    """Create average order value chart."""
    category_avg = df.groupby('category').apply(
        lambda x: x['total_revenue'].sum() / x['total_orders'].sum() if x['total_orders'].sum() > 0 else 0
    ).sort_values(ascending=False)
    
    # Map categories to colors
    category_colors = {
        'Electronics': COLORS['electronics'],
        'Home & Kitchen': COLORS['home_kitchen'],
        'Accessories': COLORS['accessories'],
        'Sports & Outdoors': COLORS['sports']
    }
    colors_map = [category_colors.get(cat, COLORS['other']) for cat in category_avg.index]
    
    bars = ax.bar(range(len(category_avg)), category_avg.values,
                  color=colors_map, alpha=0.85, edgecolor='white', linewidth=2, width=0.6)
    
    ax.set_xticks(range(len(category_avg)))
    ax.set_xticklabels(category_avg.index, rotation=0, ha='center', fontsize=11, color=COLORS['text'])
    ax.set_ylabel('Average Order Value ($)', fontsize=12, fontweight='bold', color=COLORS['text'], labelpad=12)
    ax.set_title('Average Order Value by Category', fontsize=14, fontweight='bold',
                color=COLORS['accent'], pad=20)
    ax.grid(axis='y', alpha=0.2, linestyle='--', linewidth=0.8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLORS['border'])
    ax.spines['bottom'].set_color(COLORS['border'])
    
    # Add value labels on highest bars
    max_val = category_avg.max()
    threshold = max_val * 0.2
    
    for bar, val in zip(bars, category_avg.values):
        if val > threshold:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                   f'${val:,.0f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold', color=COLORS['text'])

def create_recommendations_section(ax, df, premium_luxury, category_totals):
    """Create recommendations section with perfect alignment."""
    ax.axis('off')
    
    total_revenue = df['total_revenue'].sum()
    top_category = category_totals.index[0]
    
    # Shadow effect
    shadow = FancyBboxPatch((0.01, -0.01), 1, 1,
                           boxstyle="round,pad=0.03",
                           facecolor='black',
                           alpha=0.05,
                           transform=ax.transAxes,
                           zorder=0)
    ax.add_patch(shadow)
    
    # Background box - centered
    fancy_box = FancyBboxPatch((0, 0), 1, 1,
                              boxstyle="round,pad=0.04",
                              facecolor=COLORS['light_bg'],
                              edgecolor=COLORS['accent'],
                              linewidth=2.5,
                              alpha=0.9,
                              transform=ax.transAxes,
                              zorder=1)
    ax.add_patch(fancy_box)
    
    # Title - centered
    ax.text(0.5, 0.85, 'STRATEGIC RECOMMENDATIONS', ha='center', va='top',
           fontsize=16, fontweight='bold', color=COLORS['accent'],
           transform=ax.transAxes, zorder=2)
    
    # Divider line
    ax.plot([0.15, 0.85], [0.75, 0.75], color=COLORS['border'], 
           linewidth=1.5, transform=ax.transAxes, zorder=2)
    
    # Recommendations with icon bullets - centered alignment
    recommendations = [
        f"Focus marketing efforts on {top_category} category",
        "Expand premium product offerings in high-growth segments",
        "Leverage luxury customer base for cross-selling opportunities",
        "Develop targeted campaigns for premium product categories"
    ]
    
    y_pos = 0.60
    icons = ['📈', '💎', '🎯', '🚀']
    
    # Center the recommendations block
    start_x = 0.25  # Start position for centered text block
    
    for icon, rec in zip(icons, recommendations):
        ax.text(start_x, y_pos, f"{icon}  {rec}", ha='left', va='top',
               fontsize=11.5, color=COLORS['text'],
               transform=ax.transAxes, zorder=2)
        y_pos -= 0.12

def create_visualizations(df):
    """Create comprehensive executive-ready dashboard with perfect alignment."""
    
    # Prepare data
    category_totals = df.groupby('category')['total_revenue'].sum().sort_values(ascending=False)
    premium_luxury = df[df['price_tier'].isin(['Premium', 'Luxury'])]
    standard = df[df['price_tier'] == 'Standard']
    
    # Create figure with optimized spacing and alignment
    fig = plt.figure(figsize=(20, 14), facecolor=COLORS['background'])
    
    # Create a more structured grid with better alignment
    # Top section: Title + Summary + Metrics (aligned)
    # Middle section: Charts (aligned)
    # Bottom section: Recommendations (centered)
    
    gs = fig.add_gridspec(5, 4, 
                         hspace=0.45, wspace=0.4,
                         left=0.06, right=0.96, 
                         top=0.94, bottom=0.06,
                         height_ratios=[0.8, 1.2, 1.2, 1.0, 0.6])
    
    # Title - centered at the very top
    fig.suptitle('Customer Spending Analysis Dashboard', 
                 fontsize=24, fontweight='bold', color=COLORS['accent'], 
                 y=0.98, ha='center')
    
    # Row 0: Executive Summary + 3 Metric Cards (perfectly aligned)
    ax_summary = fig.add_subplot(gs[0, 0])
    create_executive_summary_box(ax_summary, df, premium_luxury, category_totals)
    
    total_revenue = df['total_revenue'].sum()
    avg_order_value = df['total_revenue'].sum() / df['total_orders'].sum() if df['total_orders'].sum() > 0 else 0
    top_category = category_totals.index[0]
    
    # Metric cards - aligned in a row
    ax_metric1 = fig.add_subplot(gs[0, 1])
    create_metric_card(ax_metric1, f'${total_revenue:,.0f}', 'Total Revenue', COLORS['accent'])
    
    ax_metric2 = fig.add_subplot(gs[0, 2])
    create_metric_card(ax_metric2, f'${avg_order_value:,.0f}', 'Avg Order Value', COLORS['premium'])
    
    ax_metric3 = fig.add_subplot(gs[0, 3])
    create_metric_card(ax_metric3, top_category, 'Top Category', COLORS['luxury'])
    
    # Row 1: Main Revenue Chart (spans 2 columns) + Tier Comparison + Premium Breakdown
    ax_revenue = fig.add_subplot(gs[1, :2])
    create_category_revenue_chart(ax_revenue, df, category_totals)
    
    # Tier Comparison - aligned to the right
    ax_tier = fig.add_subplot(gs[1, 2])
    create_tier_comparison_chart(ax_tier, df)
    
    # Premium/Luxury Breakdown - aligned below tier chart
    ax_premium = fig.add_subplot(gs[1, 3])
    if len(premium_luxury) > 0:
        tier_revenue = premium_luxury.groupby('price_tier')['total_revenue'].sum()
        colors_list = [COLORS[tier.lower()] if tier.lower() in COLORS else COLORS['luxury'] 
                      for tier in tier_revenue.index]
        bars = ax_premium.bar(range(len(tier_revenue)), tier_revenue.values,
                             color=colors_list, alpha=0.85, edgecolor='white', linewidth=2, width=0.6)
        ax_premium.set_xticks(range(len(tier_revenue)))
        ax_premium.set_xticklabels(tier_revenue.index, fontsize=11, fontweight='bold', color=COLORS['text'])
        ax_premium.set_ylabel('Revenue ($)', fontsize=12, fontweight='bold', color=COLORS['text'], labelpad=12)
        ax_premium.set_title('Premium/Luxury Revenue', fontsize=14, fontweight='bold',
                            color=COLORS['accent'], pad=20)
        ax_premium.grid(axis='y', alpha=0.2, linestyle='--', linewidth=0.8)
        ax_premium.spines['top'].set_visible(False)
        ax_premium.spines['right'].set_visible(False)
        ax_premium.spines['left'].set_color(COLORS['border'])
        ax_premium.spines['bottom'].set_color(COLORS['border'])
        for bar, val in zip(bars, tier_revenue.values):
            ax_premium.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                           f'${val:,.0f}', ha='center', va='bottom',
                           fontsize=11, fontweight='bold', color=COLORS['text'])
    
    # Row 2: Customer Distribution + Average Order Value (aligned side by side)
    ax_customers = fig.add_subplot(gs[2, :2])
    create_customer_distribution_chart(ax_customers, df)
    
    ax_aov = fig.add_subplot(gs[2, 2:])
    create_avg_order_value_chart(ax_aov, df)
    
    # Row 3: Recommendations (centered, full width)
    ax_rec = fig.add_subplot(gs[3, :])
    create_recommendations_section(ax_rec, df, premium_luxury, category_totals)
    
    return fig

def main():
    """Main execution function."""
    print("Loading data from database...")
    df = load_data()
    
    print(f"Loaded {len(df)} category-tier combinations")
    print(f"Categories: {df['category'].nunique()}")
    print(f"Total Revenue: ${df['total_revenue'].sum():,.2f}")
    
    print("\nCreating executive-ready visualizations...")
    fig = create_visualizations(df)
    
    # Save figure
    output_file = "customer_spending_executive_dashboard.png"
    fig.savefig(output_file, dpi=300, bbox_inches='tight', 
                facecolor=COLORS['background'], edgecolor='none')
    print(f"\n[OK] Executive dashboard saved to: {output_file}")
    
    # PDF version
    output_pdf = "customer_spending_executive_dashboard.pdf"
    fig.savefig(output_pdf, bbox_inches='tight', 
                facecolor=COLORS['background'], edgecolor='none')
    print(f"[OK] PDF version saved to: {output_pdf}")
    
    print("\nDisplaying chart...")
    try:
        plt.show()
    except Exception as e:
        print(f"Note: Could not display interactive chart: {e}")
        print("Chart saved to files. Use an image viewer to open the PNG or PDF.")

if __name__ == "__main__":
    main()

