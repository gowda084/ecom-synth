"""
E-commerce CSV to SQLite Ingestion Script
Ingests CSV files into SQLite database with automatic data type detection,
foreign key constraints, indexing, and comprehensive error handling.
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys


class CSVToSQLiteIngester:
    """Handles ingestion of CSV files into SQLite database."""
    
    def __init__(self, db_path: str = "ecommerce.db"):
        """
        Initialize the ingester.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.ingestion_stats = {}
        
    def connect(self):
        """Establish connection to SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            self.cursor = self.conn.cursor()
            print(f"[OK] Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"[ERROR] Error connecting to database: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print(f"[OK] Database connection closed")
    
    def detect_sqlite_type(self, dtype: str, sample_values: pd.Series) -> str:
        """
        Detect appropriate SQLite data type from pandas dtype and sample values.
        
        Args:
            dtype: Pandas data type
            sample_values: Sample series to analyze
            
        Returns:
            SQLite data type string
        """
        # Handle numeric types
        if pd.api.types.is_integer_dtype(dtype):
            return "INTEGER"
        elif pd.api.types.is_float_dtype(dtype):
            return "REAL"
        # Handle datetime types
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return "TEXT"  # SQLite doesn't have native datetime, store as TEXT
        # Handle boolean types
        elif pd.api.types.is_bool_dtype(dtype):
            return "INTEGER"  # SQLite uses INTEGER for boolean (0/1)
        # Handle string/object types
        elif pd.api.types.is_object_dtype(dtype):
            # Check if it's actually numeric stored as string
            try:
                pd.to_numeric(sample_values.dropna().iloc[0] if len(sample_values.dropna()) > 0 else "0")
                return "REAL"
            except (ValueError, TypeError, IndexError):
                # Check if it's a date string
                if len(sample_values.dropna()) > 0:
                    sample = str(sample_values.dropna().iloc[0])
                    try:
                        datetime.strptime(sample, "%Y-%m-%d")
                        return "TEXT"
                    except ValueError:
                        try:
                            datetime.strptime(sample, "%Y-%m-%d %H:%M:%S")
                            return "TEXT"
                        except (ValueError, TypeError):
                            pass
                return "TEXT"
        else:
            return "TEXT"  # Default to TEXT
    
    def create_table_schema(self, df: pd.DataFrame, table_name: str, 
                           primary_key: Optional[str] = None,
                           foreign_keys: Optional[List[Tuple[str, str, str]]] = None) -> str:
        """
        Generate CREATE TABLE SQL statement with automatic type detection.
        
        Args:
            df: DataFrame to analyze
            table_name: Name of the table
            primary_key: Column name for primary key
            foreign_keys: List of (column, ref_table, ref_column) tuples
            
        Returns:
            SQL CREATE TABLE statement
        """
        columns = []
        
        for col in df.columns:
            dtype = self.detect_sqlite_type(df[col].dtype, df[col])
            col_def = f'"{col}" {dtype}'
            
            # Add NOT NULL for primary key
            if col == primary_key:
                col_def += " PRIMARY KEY NOT NULL"
            
            columns.append(col_def)
        
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        create_sql += ",\n".join(f"    {col}" for col in columns)
        
        # Add foreign key constraints
        if foreign_keys:
            for fk_col, ref_table, ref_col in foreign_keys:
                create_sql += f',\n    FOREIGN KEY ("{fk_col}") REFERENCES {ref_table}("{ref_col}")'
        
        create_sql += "\n);"
        
        return create_sql
    
    def create_indexes(self, table_name: str, indexes: List[str]):
        """
        Create indexes on specified columns.
        
        Args:
            table_name: Name of the table
            indexes: List of column names to index
        """
        for col in indexes:
            index_name = f"idx_{table_name}_{col}"
            try:
                self.cursor.execute(
                    f'CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}("{col}");'
                )
            except sqlite3.Error as e:
                print(f"  ⚠ Warning: Could not create index {index_name}: {e}")
    
    def ingest_csv(self, csv_path: str, table_name: str,
                   primary_key: Optional[str] = None,
                   foreign_keys: Optional[List[Tuple[str, str, str]]] = None,
                   indexes: Optional[List[str]] = None) -> int:
        """
        Ingest a CSV file into SQLite table.
        
        Args:
            csv_path: Path to CSV file
            table_name: Name of the target table
            primary_key: Column name for primary key
            foreign_keys: List of (column, ref_table, ref_column) tuples
            indexes: List of column names to create indexes on
            
        Returns:
            Number of rows inserted
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        print(f"\n[PROCESSING] {csv_path}...")
        
        try:
            # Read CSV with error handling
            df = pd.read_csv(csv_path, encoding='utf-8')
            print(f"  [OK] Read {len(df)} rows from CSV")
            
            # Clean column names (remove any whitespace)
            df.columns = df.columns.str.strip()
            
            # Create table schema
            create_sql = self.create_table_schema(df, table_name, primary_key, foreign_keys)
            
            # Drop existing table if it exists (for re-running)
            # Temporarily disable foreign keys to allow dropping referenced tables
            self.conn.execute("PRAGMA foreign_keys = OFF")
            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            # Create table
            self.cursor.execute(create_sql)
            print(f"  [OK] Created table '{table_name}'")
            
            # Create indexes
            if indexes:
                print(f"  [OK] Creating indexes on: {', '.join(indexes)}")
                self.create_indexes(table_name, indexes)
            
            # Prepare data for insertion
            # Convert datetime columns to strings for SQLite
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].astype(str)
                elif df[col].dtype == 'object':
                    # Replace NaN with None for proper NULL handling
                    df[col] = df[col].where(pd.notnull(df[col]), None)
            
            # Insert data
            placeholders = ",".join(["?"] * len(df.columns))
            column_names = ",".join([f'"{col}"' for col in df.columns])
            insert_sql = f'INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})'
            
            rows_inserted = 0
            for idx, row in df.iterrows():
                try:
                    # Convert row to tuple, handling NaN values
                    row_values = []
                    for val in row:
                        if pd.isna(val):
                            row_values.append(None)
                        else:
                            row_values.append(val)
                    self.cursor.execute(insert_sql, tuple(row_values))
                    rows_inserted += 1
                except sqlite3.Error as e:
                    print(f"  [WARNING] Error inserting row {idx + 1}: {e}")
                    print(f"    Row data: {dict(zip(df.columns, row_values))}")
                    # Continue processing other rows
            
            self.conn.commit()
            print(f"  [OK] Inserted {rows_inserted} rows into '{table_name}'")
            
            self.ingestion_stats[table_name] = rows_inserted
            return rows_inserted
            
        except pd.errors.EmptyDataError:
            raise ValueError(f"CSV file is empty: {csv_path}")
        except pd.errors.ParserError as e:
            raise ValueError(f"Error parsing CSV file {csv_path}: {e}")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise sqlite3.Error(f"Database error while ingesting {csv_path}: {e}")
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Unexpected error while ingesting {csv_path}: {e}")
    
    def generate_summary(self):
        """Generate and display ingestion summary with statistics."""
        print("\n" + "="*70)
        print("INGESTION SUMMARY")
        print("="*70)
        
        # Total rows ingested
        total_rows = sum(self.ingestion_stats.values())
        print(f"\n[OK] Total rows ingested: {total_rows:,}")
        print(f"\nRows per table:")
        for table, count in self.ingestion_stats.items():
            print(f"  - {table}: {count:,} rows")
        
        # Most expensive product
        try:
            self.cursor.execute("""
                SELECT product_id, name, category, price, brand
                FROM Products
                ORDER BY price DESC
                LIMIT 1
            """)
            product = self.cursor.fetchone()
            if product:
                print(f"\n[MOST EXPENSIVE PRODUCT]")
                print(f"  - ID: {product[0]}")
                print(f"  - Name: {product[1]}")
                print(f"  - Category: {product[2]}")
                print(f"  - Price: ${product[3]:,.2f}")
                print(f"  - Brand: {product[4]}")
        except sqlite3.Error as e:
            print(f"\n[WARNING] Could not retrieve most expensive product: {e}")
        
        # Top customer by spending
        try:
            self.cursor.execute("""
                SELECT 
                    c.customer_id,
                    c.first_name || ' ' || c.last_name AS full_name,
                    c.city || ', ' || c.state AS location,
                    SUM(o.total_amount) AS total_spent,
                    COUNT(o.order_id) AS order_count
                FROM Customers c
                JOIN Orders o ON c.customer_id = o.customer_id
                GROUP BY c.customer_id, c.first_name, c.last_name, c.city, c.state
                ORDER BY total_spent DESC
                LIMIT 1
            """)
            customer = self.cursor.fetchone()
            if customer:
                print(f"\n[TOP CUSTOMER BY SPENDING]")
                print(f"  - ID: {customer[0]}")
                print(f"  - Name: {customer[1]}")
                print(f"  - Location: {customer[2]}")
                print(f"  - Total Spent: ${customer[3]:,.2f}")
                print(f"  - Number of Orders: {customer[4]}")
        except sqlite3.Error as e:
            print(f"\n[WARNING] Could not retrieve top customer: {e}")
        
        # Additional statistics
        try:
            # Total revenue
            self.cursor.execute("SELECT SUM(total_amount) FROM Orders")
            total_revenue = self.cursor.fetchone()[0] or 0
            print(f"\n[TOTAL REVENUE] ${total_revenue:,.2f}")
            
            # Average order value
            self.cursor.execute("SELECT AVG(total_amount) FROM Orders")
            avg_order = self.cursor.fetchone()[0] or 0
            print(f"[AVERAGE ORDER VALUE] ${avg_order:,.2f}")
            
            # Product categories count
            self.cursor.execute("SELECT COUNT(DISTINCT category) FROM Products")
            category_count = self.cursor.fetchone()[0] or 0
            print(f"[PRODUCT CATEGORIES] {category_count}")
            
            # Payment methods distribution
            self.cursor.execute("""
                SELECT payment_method, COUNT(*) as count
                FROM Payments
                GROUP BY payment_method
                ORDER BY count DESC
            """)
            payment_methods = self.cursor.fetchall()
            if payment_methods:
                print(f"\n[PAYMENT METHODS DISTRIBUTION]")
                for method, count in payment_methods:
                    print(f"  - {method}: {count} transactions")
            
        except sqlite3.Error as e:
            print(f"\n[WARNING] Could not retrieve additional statistics: {e}")
        
        print("\n" + "="*70)


def main():
    """Main execution function."""
    print("E-commerce CSV to SQLite Ingestion")
    print("="*70)
    
    ingester = CSVToSQLiteIngester("ecommerce.db")
    
    try:
        # Connect to database
        ingester.connect()
        
        # Define ingestion order (respecting foreign key dependencies)
        ingestion_config = [
            {
                "csv": "Products.csv",
                "table": "Products",
                "primary_key": "product_id",
                "foreign_keys": None,
                "indexes": ["category", "brand", "price"]
            },
            {
                "csv": "Customers.csv",
                "table": "Customers",
                "primary_key": "customer_id",
                "foreign_keys": None,
                "indexes": ["city", "state", "country", "loyalty_points"]
            },
            {
                "csv": "Orders.csv",
                "table": "Orders",
                "primary_key": "order_id",
                "foreign_keys": [("customer_id", "Customers", "customer_id")],
                "indexes": ["customer_id", "order_date", "status", "total_amount"]
            },
            {
                "csv": "Order_Items.csv",
                "table": "Order_Items",
                "primary_key": "order_item_id",
                "foreign_keys": [
                    ("order_id", "Orders", "order_id"),
                    ("product_id", "Products", "product_id")
                ],
                "indexes": ["order_id", "product_id"]
            },
            {
                "csv": "Payments.csv",
                "table": "Payments",
                "primary_key": "payment_id",
                "foreign_keys": [("order_id", "Orders", "order_id")],
                "indexes": ["order_id", "payment_method", "status", "payment_date"]
            }
        ]
        
        # Ingest all CSV files
        for config in ingestion_config:
            ingester.ingest_csv(
                csv_path=config["csv"],
                table_name=config["table"],
                primary_key=config["primary_key"],
                foreign_keys=config["foreign_keys"],
                indexes=config["indexes"]
            )
        
        # Generate summary
        ingester.generate_summary()
        
        print("\n[SUCCESS] Ingestion completed successfully!")
        print(f"[INFO] Database saved to: {ingester.db_path}")
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except sqlite3.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        ingester.close()


if __name__ == "__main__":
    main()

