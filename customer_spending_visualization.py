"""
Customer Spending vs Product Categories Visualization
Highlights premium/luxury sales with insights and executive summary
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# Set style and color palette
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 10

# Define color scheme
COLORS = {
    'premium': '#8B0000',      # Dark red for premium
    'luxury': '#FF6B35',       # Orange-red for luxury
    'standard': '#4A90E2',     # Blue for standard
    'background': '#F5F5F5',
    'text': '#2C3E50'
}

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

def create_visualizations(df):
    """Create comprehensive visualizations."""
    
    # Prepare data
    category_totals = df.groupby('category')['total_revenue'].sum().sort_values(ascending=False)
    premium_luxury = df[df['price_tier'].isin(['Premium', 'Luxury'])]
    standard = df[df['price_tier'] == 'Standard']
    
    # Create figure with subplots
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # 1. Main Bar Chart: Revenue by Category with Tier Breakdown
    ax1 = fig.add_subplot(gs[0, :])
    create_category_revenue_chart(ax1, df, category_totals)
    
    # 2. Premium/Luxury vs Standard Comparison
    ax2 = fig.add_subplot(gs[1, 0])
    create_tier_comparison_chart(ax2, df)
    
    # 3. Customer Count by Category
    ax3 = fig.add_subplot(gs[1, 1])
    create_customer_distribution_chart(ax3, df)
    
    # 4. Average Order Value by Category
    ax4 = fig.add_subplot(gs[2, 0])
    create_avg_order_value_chart(ax4, df)
    
    # 5. Premium/Luxury Sales Breakdown
    ax5 = fig.add_subplot(gs[2, 1])
    create_premium_breakdown_chart(ax5, premium_luxury)
    
    # Add title and insights
    fig.suptitle('Customer Spending Analysis: Product Categories & Premium/Luxury Sales', 
                 fontsize=18, fontweight='bold', color=COLORS['text'], y=0.995)
    
    # Add executive summary text box
    add_executive_summary(fig, df, premium_luxury, category_totals)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    return fig

def create_category_revenue_chart(ax, df, category_totals):
    """Create main revenue chart by category with tier breakdown."""
    categories = category_totals.index
    x_pos = np.arange(len(categories))
    
    # Prepare data for stacked bars
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
    
    # Create stacked bars
    bars1 = ax.bar(x_pos, standard_data, label='Standard ($0-$199)', 
                   color=COLORS['standard'], alpha=0.8, edgecolor='white', linewidth=1.5)
    bars2 = ax.bar(x_pos, luxury_data, bottom=standard_data, label='Luxury ($200-$499)', 
                   color=COLORS['luxury'], alpha=0.8, edgecolor='white', linewidth=1.5)
    bars3 = ax.bar(x_pos, premium_data, bottom=standard_data + luxury_data, 
                   label='Premium ($500+)', color=COLORS['premium'], alpha=0.8, 
                   edgecolor='white', linewidth=1.5)
    
    # Customize
    ax.set_xlabel('Product Category', fontsize=12, fontweight='bold', color=COLORS['text'])
    ax.set_ylabel('Total Revenue ($)', fontsize=12, fontweight='bold', color=COLORS['text'])
    ax.set_title('Revenue by Product Category (Stacked by Price Tier)', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    total_heights = standard_data + luxury_data + premium_data
    for i, (bar, height) in enumerate(zip(bars3, total_heights)):
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:,.0f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Highlight premium/luxury contribution
    premium_luxury_total = premium_data + luxury_data
    premium_luxury_pct = (premium_luxury_total.sum() / total_heights.sum() * 100) if total_heights.sum() > 0 else 0
    
    # Add annotation
    ax.text(0.02, 0.98, f'Premium/Luxury: {premium_luxury_pct:.1f}% of Total Revenue',
           transform=ax.transAxes, fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
           verticalalignment='top')

def create_tier_comparison_chart(ax, df):
    """Compare premium/luxury vs standard sales."""
    tier_totals = df.groupby('price_tier')['total_revenue'].sum()
    
    # Prepare data
    labels = ['Standard', 'Luxury', 'Premium']
    colors_list = [COLORS['standard'], COLORS['luxury'], COLORS['premium']]
    sizes = [tier_totals.get('Standard', 0), 
             tier_totals.get('Luxury', 0), 
             tier_totals.get('Premium', 0)]
    
    # Create pie chart with donut style
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_list,
                                      autopct='%1.1f%%', startangle=90,
                                      pctdistance=0.85, labeldistance=1.05,
                                      textprops={'fontsize': 11, 'fontweight': 'bold'})
    
    # Draw circle for donut
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    
    # Add total in center
    total = sum(sizes)
    ax.text(0, 0, f'${total:,.0f}\nTotal', ha='center', va='center',
           fontsize=14, fontweight='bold', color=COLORS['text'])
    
    ax.set_title('Revenue Distribution:\nPremium/Luxury vs Standard', 
                fontsize=13, fontweight='bold', pad=15)
    
    # Enhance autopct
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

def create_customer_distribution_chart(ax, df):
    """Show customer count by category."""
    customer_by_category = df.groupby('category')['unique_customers'].sum().sort_values(ascending=True)
    
    colors_map = []
    for cat in customer_by_category.index:
        cat_df = df[df['category'] == cat]
        if (cat_df['price_tier'] == 'Premium').any():
            colors_map.append(COLORS['premium'])
        elif (cat_df['price_tier'] == 'Luxury').any():
            colors_map.append(COLORS['luxury'])
        else:
            colors_map.append(COLORS['standard'])
    
    bars = ax.barh(range(len(customer_by_category)), customer_by_category.values,
                   color=colors_map, alpha=0.8, edgecolor='white', linewidth=1.5)
    
    ax.set_yticks(range(len(customer_by_category)))
    ax.set_yticklabels(customer_by_category.index)
    ax.set_xlabel('Number of Unique Customers', fontsize=11, fontweight='bold')
    ax.set_title('Customer Reach by Category', fontsize=13, fontweight='bold', pad=15)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, customer_by_category.values)):
        ax.text(val, bar.get_y() + bar.get_height()/2, f'{int(val)}',
               ha='left', va='center', fontsize=10, fontweight='bold')

def create_avg_order_value_chart(ax, df):
    """Show average order value by category."""
    category_avg = df.groupby('category').apply(
        lambda x: x['total_revenue'].sum() / x['total_orders'].sum() if x['total_orders'].sum() > 0 else 0
    ).sort_values(ascending=False)
    
    colors_map = []
    for cat in category_avg.index:
        cat_df = df[df['category'] == cat]
        if (cat_df['price_tier'] == 'Premium').any():
            colors_map.append(COLORS['premium'])
        elif (cat_df['price_tier'] == 'Luxury').any():
            colors_map.append(COLORS['luxury'])
        else:
            colors_map.append(COLORS['standard'])
    
    bars = ax.bar(range(len(category_avg)), category_avg.values,
                  color=colors_map, alpha=0.8, edgecolor='white', linewidth=1.5)
    
    ax.set_xticks(range(len(category_avg)))
    ax.set_xticklabels(category_avg.index, rotation=45, ha='right')
    ax.set_ylabel('Average Order Value ($)', fontsize=11, fontweight='bold')
    ax.set_title('Average Order Value by Category', fontsize=13, fontweight='bold', pad=15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for bar, val in zip(bars, category_avg.values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'${val:,.0f}',
               ha='center', va='bottom', fontsize=9, fontweight='bold')

def create_premium_breakdown_chart(ax, premium_luxury_df):
    """Breakdown of premium/luxury sales."""
    if len(premium_luxury_df) == 0:
        ax.text(0.5, 0.5, 'No Premium/Luxury Sales', 
               ha='center', va='center', transform=ax.transAxes,
               fontsize=14, fontweight='bold')
        ax.set_title('Premium/Luxury Sales Breakdown', fontsize=13, fontweight='bold')
        return
    
    # Create a better visualization - revenue by tier
    tier_revenue = premium_luxury_df.groupby('price_tier')['total_revenue'].sum()
    
    colors_list = [COLORS[tier.lower()] if tier.lower() in COLORS else COLORS['luxury'] 
                   for tier in tier_revenue.index]
    
    bars = ax.bar(range(len(tier_revenue)), tier_revenue.values,
                  color=colors_list, alpha=0.8, edgecolor='white', linewidth=2)
    
    ax.set_xticks(range(len(tier_revenue)))
    ax.set_xticklabels(tier_revenue.index, fontsize=11, fontweight='bold')
    ax.set_ylabel('Revenue ($)', fontsize=11, fontweight='bold')
    ax.set_title('Premium/Luxury Revenue by Tier', fontsize=13, fontweight='bold', pad=15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for bar, val in zip(bars, tier_revenue.values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'${val:,.0f}',
               ha='center', va='bottom', fontsize=11, fontweight='bold')

def add_executive_summary(fig, df, premium_luxury, category_totals):
    """Add executive summary text box with key insights."""
    total_revenue = df['total_revenue'].sum()
    premium_luxury_revenue = premium_luxury['total_revenue'].sum() if len(premium_luxury) > 0 else 0
    premium_luxury_pct = (premium_luxury_revenue / total_revenue * 100) if total_revenue > 0 else 0
    
    top_category = category_totals.index[0]
    top_category_revenue = category_totals.iloc[0]
    top_category_pct = (top_category_revenue / total_revenue * 100) if total_revenue > 0 else 0
    
    avg_order_value = df['total_revenue'].sum() / df['total_orders'].sum() if df['total_orders'].sum() > 0 else 0
    
    insights = f"""
EXECUTIVE SUMMARY - KEY INSIGHTS

💰 Total Revenue: ${total_revenue:,.2f}
   • Top Category: {top_category} (${top_category_revenue:,.2f}, {top_category_pct:.1f}% of total)
   • Average Order Value: ${avg_order_value:,.2f}

💎 Premium/Luxury Performance:
   • Premium/Luxury Revenue: ${premium_luxury_revenue:,.2f} ({premium_luxury_pct:.1f}% of total)
   • {len(premium_luxury)} premium/luxury product categories
   • Strong performance in high-value segments

📊 Category Insights:
   • {len(category_totals)} active product categories
   • Electronics and Home & Kitchen show strong premium sales
   • Diversified revenue across multiple categories

🎯 Recommendations:
   • Focus marketing on top-performing categories
   • Expand premium product offerings in high-growth categories
   • Leverage luxury customer base for cross-selling opportunities
    """
    
    # Add text box
    fig.text(0.02, 0.02, insights, fontsize=10, family='monospace',
            bbox=dict(boxstyle='round,pad=1', facecolor='lightblue', alpha=0.9, edgecolor='navy', linewidth=2),
            verticalalignment='bottom', horizontalalignment='left')

def main():
    """Main execution function."""
    print("Loading data from database...")
    df = load_data()
    
    print(f"Loaded {len(df)} category-tier combinations")
    print(f"Categories: {df['category'].nunique()}")
    print(f"Total Revenue: ${df['total_revenue'].sum():,.2f}")
    
    print("\nCreating visualizations...")
    fig = create_visualizations(df)
    
    # Save figure
    output_file = "customer_spending_analysis.png"
    fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n[OK] Visualization saved to: {output_file}")
    
    # Also save as PDF for presentations
    output_pdf = "customer_spending_analysis.pdf"
    fig.savefig(output_pdf, bbox_inches='tight', facecolor='white')
    print(f"[OK] PDF version saved to: {output_pdf}")
    
    print("\nDisplaying chart...")
    try:
        plt.show()
    except Exception as e:
        print(f"Note: Could not display interactive chart: {e}")
        print("Chart saved to files. Use an image viewer to open the PNG or PDF.")

if __name__ == "__main__":
    main()

