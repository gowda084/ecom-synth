"""Simple demonstration of the customer spending report."""
import sqlite3
import pandas as pd

# Read and execute the query
conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

with open('customer_spending_report.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Extract main query
main_query = sql_content.split('/*')[0]
lines = []
in_query = False
for line in main_query.split('\n'):
    stripped = line.strip()
    if stripped.upper().startswith('WITH') or (stripped.upper().startswith('SELECT') and not in_query):
        in_query = True
    if in_query and not stripped.startswith('--'):
        lines.append(line)

query = '\n'.join(lines).strip()

# Execute
cursor.execute(query)
columns = [desc[0] for desc in cursor.description]
results = cursor.fetchall()
df = pd.DataFrame(results, columns=columns)

# Display results
print("=" * 80)
print("CUSTOMER SPENDING DASHBOARD REPORT")
print("=" * 80)
print(f"\nTotal Customers: {len(df)}")
print(f"Total Revenue: ${df['Total Spending'].sum():,.2f}")
print(f"Average Customer Spending: ${df['Total Spending'].mean():,.2f}")

# Luxury customers
luxury = df[df['Customer Tier'].str.contains('Luxury|Premium', na=False)]
print(f"\nLuxury/Premium Customers: {len(luxury)}")
print(f"  Total Luxury Revenue: ${luxury['Total Spending'].sum():,.2f}")

# Top 5
print("\n" + "=" * 80)
print("TOP 5 CUSTOMERS BY SPENDING")
print("=" * 80)
top5_cols = ['Customer Name', 'Total Spending', 'Order Frequency', 
             'Average Order Value', 'Most Expensive Product Name', 'Customer Tier']
print(df.head(5)[top5_cols].to_string(index=False))

conn.close()

