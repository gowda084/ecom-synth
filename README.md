E-Commerce Customer Spending Analysis Dashboard

Overview
This project uses Cursor IDE’s AI-assisted development to build a powerful and visually engaging dashboard for analyzing customer spending within an e-commerce environment. The workflow includes synthetic data generation, SQLite ingestion, advanced SQL analytics, and executive-quality visualizations for premium/luxury purchase insights.

Features
- Realistic synthetic e-commerce dataset generation (Products, Customers, Orders, Order_Items, Payments)
- Automated data ingestion into a relational SQLite database
- Advanced SQL analytics for customer-level spending insights
- Clean, modern, executive-ready dashboard visualizations
- Repeatable, prompt-driven workflow via Cursor IDE

Getting Started
Prerequisites
- Cursor IDE
- Python 3.8+
- SQLite3
- Git

Installation
1. Clone this repository:
    git clone https://github.com/gowda084/ecom-synth.git
    cd ecom-synth

2. Install required dependencies:
    pip install -r requirements.txt

3. Open the folder in Cursor IDE

Cursor IDE Prompts

1. Generate Synthetic E-Commerce Data
Prompt: Generate five CSV files with realistic synthetic e-commerce data for the following tables: Products, Customers, Orders, Order_Items, Payments. Each dataset should include diverse entries, with products featuring multiple categories, premium pricing, and detailed descriptions. Add customer avatars, locations, and loyalty points. Orders should include bulk and premium purchases to reflect high-value transactions.

2. Ingest Data into SQLite
Prompt: Write Python code to ingest the generated CSV files into corresponding SQLite tables. Use robust error handling, automatic data type detection, and display a summary after ingestion (number of rows, highlight the most expensive products, top customer spending). Ensure schema uses foreign keys and indexing for query efficiency.

3. Advanced SQL Analytics
Prompt: Generate an SQL query joining Customers, Orders, Order_Items, Products, and Payments to output customer total spending, most expensive product purchased, order frequency, and luxury/premium segment participation. Sort by top spenders and present results with calculated average order value and clear column aliases.

4. Executive Dashboard Visualization
Prompt: Refactor the customer spending analysis dashboard to be visually attractive, executive-ready, and clutter-free. Use a minimalist modern color palette, proper spacing, readable fonts, clear chart titles and labels, highlight cards for total revenue and top categories, and position the executive summary in a clean overlay box. Add a recommendations section with icon bullets at the bottom.

Project Structure
data/                      - Synthetic data files (CSV)
scripts/                   - Data generation & ingestion scripts
dashboard/                 - Visualization and analytics scripts
prompts/                   - Cursor IDE prompts used for the project
database/                  - SQLite database & schema
README.md

Usage
- Customize or extend the Cursor IDE prompts for different analytics needs
- Modify SQL queries to expand business use cases
- Use dashboard outputs for presentations, insights, and stakeholder reports

