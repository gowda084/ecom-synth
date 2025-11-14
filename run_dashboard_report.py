"""
Run the customer dashboard report and display formatted results.
"""

import sqlite3
import pandas as pd

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False
    print("Note: 'tabulate' not installed. Install with 'pip install tabulate' for better formatting.")

def run_dashboard_report(db_path="ecommerce.db", sql_file="customer_dashboard_report.sql"):
    """
    Execute the dashboard report SQL query and display results.
    
    Args:
        db_path: Path to SQLite database
        sql_file: Path to SQL file containing the query
    """
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        # Read SQL query
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Extract the main query (before alternative queries section)
        # Split by the alternative query marker
        if '-- ============================================================================' in sql_content:
            parts = sql_content.split('-- ============================================================================')
            # Take the first part (main query) and the second part (which has the alternative)
            # But we only want the main query, so find where the alternative starts
            if '/*' in sql_content:
                main_query = sql_content.split('/*')[0]
            else:
                main_query = parts[0] if len(parts) > 0 else sql_content
        else:
            main_query = sql_content.split('/*')[0] if '/*' in sql_content else sql_content
        
        # Remove comment lines (lines starting with --)
        lines = []
        for line in main_query.split('\n'):
            stripped = line.strip()
            # Keep the line if it's not a comment or is empty (we'll filter empty later)
            if not stripped.startswith('--'):
                lines.append(line)
        
        query = '\n'.join(lines).strip()
        
        # If query is empty, try a different approach - just remove comment markers
        if not query or len(query) < 50:
            # Fallback: remove only full-line comments
            lines = []
            for line in sql_content.split('\n'):
                if line.strip() and not line.strip().startswith('--'):
                    if '/*' not in line:  # Skip lines with block comment start
                        lines.append(line)
            query = '\n'.join(lines).split('/*')[0].strip()
        
        # Execute query
        print("=" * 100)
        print("E-COMMERCE CUSTOMER DASHBOARD REPORT")
        print("=" * 100)
        print("\nExecuting query...\n")
        
        # Execute query using cursor first to check for errors
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            # Get column names
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                results = cursor.fetchall()
                # Convert to DataFrame
                if len(results) > 0:
                    df = pd.DataFrame(results, columns=columns)
                else:
                    print("Query returned 0 rows. Checking query logic...")
                    # Test individual CTEs
                    test_query = "WITH CustomerOrderSummary AS (SELECT customer_id, SUM(total_amount) AS total_spending, COUNT(order_id) AS order_count FROM Orders GROUP BY customer_id) SELECT COUNT(*) FROM CustomerOrderSummary"
                    cursor.execute(test_query)
                    print(f"CustomerOrderSummary CTE: {cursor.fetchone()[0]} rows")
                    df = pd.DataFrame()  # Empty DataFrame
            else:
                print("Error: Query returned no description (possible syntax error)")
                df = pd.DataFrame()
        except sqlite3.Error as sql_err:
            print(f"SQL Error: {sql_err}")
            raise
        
        # Display results
        if len(df) > 0 and not df.empty:
            print(f"Found {len(df)} customers with orders\n")
            
            # Display full results in a formatted table
            if HAS_TABULATE:
                print(tabulate(df, headers='keys', tablefmt='grid', showindex=False, floatfmt='.2f'))
            else:
                # Fallback to pandas display
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', None)
                pd.set_option('display.max_colwidth', 30)
                print(df.to_string(index=False))
            
            # Summary statistics
            print("\n" + "=" * 100)
            print("SUMMARY STATISTICS")
            print("=" * 100)
            print(f"Total Customers: {len(df)}")
            print(f"Total Revenue: ${df['Total Spending'].sum():,.2f}")
            print(f"Average Customer Spending: ${df['Total Spending'].mean():,.2f}")
            print(f"Median Customer Spending: ${df['Total Spending'].median():,.2f}")
            print(f"Highest Spending: ${df['Total Spending'].max():,.2f}")
            print(f"Average Order Frequency: {df['Order Frequency'].mean():.1f} orders")
            print(f"Average Order Value: ${df['Average Order Value'].mean():,.2f}")
            
            # Luxury customers
            luxury_customers = df[df['Purchase Tier'].isin(['Premium', 'Luxury'])]
            print(f"\nLuxury Customers (Premium/Luxury tier): {len(luxury_customers)}")
            if len(luxury_customers) > 0:
                print(f"  Average Spending: ${luxury_customers['Total Spending'].mean():,.2f}")
                print(f"  Total Luxury Revenue: ${luxury_customers['Total Spending'].sum():,.2f}")
            
            # Top 10 customers
            print("\n" + "=" * 100)
            print("TOP 10 CUSTOMERS BY SPENDING")
            print("=" * 100)
            top_10 = df.head(10)[['Customer Name', 'Location', 'Total Spending', 
                                  'Order Frequency', 'Average Order Value', 
                                  'Most Expensive Product Name', 'Purchase Tier']]
            if HAS_TABULATE:
                print(tabulate(top_10, headers='keys', tablefmt='grid', showindex=False, floatfmt='.2f'))
            else:
                print(top_10.to_string(index=False))
            
        else:
            print("No results found.")
        
        conn.close()
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_dashboard_report()

