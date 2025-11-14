-- ============================================================================
-- E-commerce Customer Dashboard Report
-- ============================================================================
-- This query joins Customers, Orders, Order_Items, Products, and Payments
-- to generate a comprehensive customer spending analysis report.
-- ============================================================================

WITH CustomerOrderSummary AS (
    -- Get distinct order totals per customer to avoid double counting
    SELECT 
        customer_id,
        SUM(total_amount) AS total_spending,
        COUNT(order_id) AS order_count,
        SUM(discount_amount) AS total_discounts,
        SUM(shipping_cost) AS total_shipping,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
        SUM(CASE WHEN status = 'Shipped' THEN 1 ELSE 0 END) AS shipped_orders,
        SUM(CASE WHEN status = 'Processing' THEN 1 ELSE 0 END) AS processing_orders
    FROM Orders
    GROUP BY customer_id
),
CustomerProductStats AS (
    -- Get product-related statistics per customer
    SELECT 
        o.customer_id,
        MAX(p.price) AS max_product_price,
        COUNT(DISTINCT p.category) AS categories_purchased,
        COUNT(DISTINCT oi.product_id) AS unique_products_purchased,
        COUNT(DISTINCT CASE WHEN p.price >= 500 THEN oi.order_item_id END) AS premium_purchases,
        COUNT(DISTINCT CASE WHEN p.price >= 200 THEN oi.order_item_id END) AS luxury_purchases,
        SUM(oi.quantity) AS total_items_purchased,
        AVG(oi.quantity) AS avg_items_per_order_item
    FROM Orders o
    JOIN Order_Items oi ON o.order_id = oi.order_id
    JOIN Products p ON oi.product_id = p.product_id
    GROUP BY o.customer_id
),
CustomerPaymentStats AS (
    -- Get payment-related statistics per customer
    SELECT 
        o.customer_id,
        COUNT(DISTINCT pay.payment_id) AS payment_count,
        GROUP_CONCAT(DISTINCT pay.payment_method) AS payment_methods
    FROM Orders o
    LEFT JOIN Payments pay ON o.order_id = pay.order_id
    GROUP BY o.customer_id
)

SELECT 
    -- Customer Identification
    c.customer_id AS "Customer ID",
    c.first_name || ' ' || c.last_name AS "Customer Name",
    c.email AS "Email",
    c.city || ', ' || c.state AS "Location",
    c.loyalty_points AS "Loyalty Points",
    
    -- Spending Metrics
    ROUND(cos.total_spending, 2) AS "Total Spending",
    cos.order_count AS "Order Frequency",
    ROUND(cos.total_spending / NULLIF(cos.order_count, 0), 2) AS "Average Order Value",
    
    -- Most Expensive Product Purchased
    ROUND(cps.max_product_price, 2) AS "Most Expensive Product Price",
    (SELECT p2.name 
     FROM Products p2
     JOIN Order_Items oi2 ON p2.product_id = oi2.product_id
     JOIN Orders o2 ON oi2.order_id = o2.order_id
     WHERE o2.customer_id = c.customer_id
     ORDER BY p2.price DESC
     LIMIT 1) AS "Most Expensive Product Name",
    
    (SELECT p2.category 
     FROM Products p2
     JOIN Order_Items oi2 ON p2.product_id = oi2.product_id
     JOIN Orders o2 ON oi2.order_id = o2.order_id
     WHERE o2.customer_id = c.customer_id
     ORDER BY p2.price DESC
     LIMIT 1) AS "Most Expensive Product Category",
    
    -- Luxury Purchase Indicators
    CASE 
        WHEN cps.max_product_price >= 500 THEN 'Premium'
        WHEN cps.max_product_price >= 200 THEN 'Luxury'
        ELSE 'Standard'
    END AS "Purchase Tier",
    
    cps.premium_purchases AS "Premium Purchases Count",
    cps.luxury_purchases AS "Luxury Purchases Count",
    
    -- Product Diversity
    cps.categories_purchased AS "Categories Purchased",
    cps.unique_products_purchased AS "Unique Products Purchased",
    
    -- Payment Information
    cpay.payment_count AS "Payment Transactions",
    cpay.payment_methods AS "Payment Methods Used",
    
    -- Order Status Summary
    cos.delivered_orders AS "Delivered Orders",
    cos.shipped_orders AS "Shipped Orders",
    cos.processing_orders AS "Processing Orders",
    
    -- Date Range
    cos.first_order_date AS "First Order Date",
    cos.last_order_date AS "Last Order Date",
    
    -- Additional Calculated Metrics
    ROUND(cps.total_items_purchased, 0) AS "Total Items Purchased",
    ROUND(cps.avg_items_per_order_item, 2) AS "Average Items Per Order",
    ROUND(cos.total_discounts, 2) AS "Total Discounts Received",
    ROUND(cos.total_shipping, 2) AS "Total Shipping Costs"

FROM 
    Customers c
    INNER JOIN CustomerOrderSummary cos ON c.customer_id = cos.customer_id
    LEFT JOIN CustomerProductStats cps ON c.customer_id = cps.customer_id
    LEFT JOIN CustomerPaymentStats cpay ON c.customer_id = cpay.customer_id

WHERE 
    cos.order_count > 0

ORDER BY 
    "Total Spending" DESC,
    "Order Frequency" DESC,
    "Most Expensive Product Price" DESC;

-- ============================================================================
-- Alternative Query: Luxury Customers Only
-- ============================================================================
-- Uncomment below to see only customers with luxury purchases (products >= $200)

/*
SELECT 
    c.customer_id AS "Customer ID",
    c.first_name || ' ' || c.last_name AS "Customer Name",
    c.city || ', ' || c.state AS "Location",
    ROUND(SUM(DISTINCT o.total_amount), 2) AS "Total Spending",
    COUNT(DISTINCT o.order_id) AS "Order Frequency",
    MAX(p.price) AS "Most Expensive Product Price",
    (SELECT p2.name 
     FROM Products p2
     JOIN Order_Items oi2 ON p2.product_id = oi2.product_id
     JOIN Orders o2 ON oi2.order_id = o2.order_id
     WHERE o2.customer_id = c.customer_id
     ORDER BY p2.price DESC
     LIMIT 1) AS "Most Expensive Product",
    COUNT(DISTINCT CASE WHEN p.price >= 200 THEN oi.order_item_id END) AS "Luxury Items Purchased"
FROM 
    Customers c
    JOIN Orders o ON c.customer_id = o.customer_id
    JOIN Order_Items oi ON o.order_id = oi.order_id
    JOIN Products p ON oi.product_id = p.product_id
GROUP BY 
    c.customer_id, c.first_name, c.last_name, c.city, c.state
HAVING 
    MAX(p.price) >= 200
ORDER BY 
    "Total Spending" DESC;
*/

