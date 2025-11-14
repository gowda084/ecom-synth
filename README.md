E-Commerce Customer Spending Analysis Dashboard
Overview
This project leverages Cursor IDE’s AI development tools to create a powerful and visually appealing dashboard for analyzing customer spending in an e-commerce environment. The workflow covers data generation, ingestion, SQL analytics, and publication-quality visualization of premium/luxury sales trends.

Features
1.Auto-generation of realistic e-commerce data (Products, Customers, Orders, Order_Items, Payments)

2.Data ingestion and relational storage with SQLite

3.Rich SQL analytics and executive summary outputs

4.Visually modern, stakeholder-ready dashboard

5.All steps managed with clear Cursor IDE prompts

Getting Started
1.Prerequisites
2.Cursor IDE
3.Python 3.8+
4.SQLite3 (bundled with Python or available separately)
5.Git

Installation
1.Clone this repo:
bash
git clone https://github.com/yourusername/ecom-analytics-dashboard.git
cd ecom-analytics-dashboard

2.Install dependencies:
bash
pip install -r requirements.txt

3.Open the project in Cursor IDE.

Cursor IDE Prompts
1. Generate Synthetic E-Commerce Data
text
Prompt: Generate five CSV files with realistic synthetic e-commerce data for the following tables: Products, Customers, Orders, Order_Items, Payments. Each dataset should include diverse entries, with products featuring multiple categories, premium pricing, and detailed descriptions. Add customer avatars, locations, and loyalty points. Orders should include bulk and premium purchases to reflect high-value transactions.
2. Ingest Data into SQLite
text
Prompt: Write Python code to ingest the generated CSV files into corresponding SQLite tables. Use robust error handling, automatic data type detection, and display a summary after ingestion (number of rows, highlight the most expensive products, top customer spending). Ensure schema uses foreign keys and indexing for query efficiency.
3. Advanced SQL Analytics
text
Prompt: Generate an SQL query joining Customers, Orders, Order_Items, Products, and Payments to output customer total spending, most expensive product purchased, order frequency, and luxury/premium segment participation. Sort by top spenders and present results with calculated average order value and clear column aliases.
4. Executive Dashboard Visualization
text
Prompt: Refactor the customer spending analysis dashboard to be visually attractive, executive-ready, and clutter-free. Use a minimalist modern color palette, proper spacing, readable fonts, clear chart titles and labels, highlight cards for total revenue and top categories, and position the executive summary in a clean overlay box. Add a recommendations section with icon bullets at the bottom.

Project Structure
text
├── data/                      # Synthetic data files (CSV)
├── scripts/                   # Data generation & ingestion scripts
├── dashboard/                 # Visualization and analytics scripts
├── prompts/                   # Cursor IDE prompts used for the project
├── database/                  # SQLite database & schema
├── README.md

Usage
1.Modify prompts in the Cursor IDE for custom analysis or styling.

2.Extend SQL and Python scripts as your business case demands.

3.Use dashboard outputs in executive and stakeholder presentations.
