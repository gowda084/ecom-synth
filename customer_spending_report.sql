-- ============================================================================
-- Customer Spending Dashboard Report
-- ============================================================================
-- Joins all tables to show customer spending, luxury purchases, and order metrics
-- Uses CTEs to properly calculate totals without double-counting
-- ============================================================================

WITH CustomerOrders AS (
    -- Get order totals per customer (one row per order)
    SELECT 
        customer_id,
        SUM(total_amount) AS total_spending,
        COUNT(order_id) AS order_count,
        MIN(order_date) AS first_purchase,
        MAX(order_date) AS last_purchase
    FROM Orders
    GROUP BY customer_id
),
CustomerProducts AS (
    -- Get product statistics per customer
    SELECT 
        o.customer_id,
        MAX(p.price) AS max_price,
        COUNT(DISTINCT p.category) AS categories_count,
        COUNT(DISTINCT CASE WHEN p.price >= 500 THEN oi.order_item_id END) AS premium_count,
        COUNT(DISTINCT CASE WHEN p.price >= 200 THEN oi.order_item_id END) AS luxury_count
    FROM Orders o
    JOIN Order_Items oi ON o.order_id = oi.order_id
    JOIN Products p ON oi.product_id = p.product_id
    GROUP BY o.customer_id
)

SELECT 
    -- Customer Information
    c.customer_id AS "Customer ID",
    c.first_name || ' ' || c.last_name AS "Customer Name",
    c.city || ', ' || c.state AS "Location",
    c.loyalty_points AS "Loyalty Points",
    
    -- Spending Metrics
    ROUND(co.total_spending, 2) AS "Total Spending",
    co.order_count AS "Order Frequency",
    ROUND(co.total_spending / NULLIF(co.order_count, 0), 2) AS "Average Order Value",
    
    -- Most Expensive Product Purchased
    ROUND(cp.max_price, 2) AS "Most Expensive Product Price",
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
     LIMIT 1) AS "Product Category",
    
    -- Luxury Purchase Indicators
    CASE 
        WHEN cp.max_price >= 500 THEN 'Premium Customer'
        WHEN cp.max_price >= 200 THEN 'Luxury Customer'
        ELSE 'Standard Customer'
    END AS "Customer Tier",
    
    cp.premium_count AS "Premium Items Count",
    cp.luxury_count AS "Luxury Items Count",
    
    -- Additional Metrics
    cp.categories_count AS "Categories Purchased",
    co.first_purchase AS "First Purchase Date",
    co.last_purchase AS "Last Purchase Date"

FROM 
    Customers c
    INNER JOIN CustomerOrders co ON c.customer_id = co.customer_id
    LEFT JOIN CustomerProducts cp ON c.customer_id = cp.customer_id

WHERE 
    co.order_count > 0

ORDER BY 
    "Total Spending" DESC,
    "Most Expensive Product Price" DESC,
    "Order Frequency" DESC;

-- ============================================================================
-- Luxury Customers Only View
-- ============================================================================
-- Uncomment to see only customers who made luxury purchases (>= $200)

/*
SELECT 
    c.customer_id AS "Customer ID",
    c.first_name || ' ' || c.last_name AS "Customer Name",
    c.city || ', ' || c.state AS "Location",
    ROUND(SUM(DISTINCT o.total_amount), 2) AS "Total Spending",
    COUNT(DISTINCT o.order_id) AS "Order Frequency",
    ROUND(SUM(DISTINCT o.total_amount) / NULLIF(COUNT(DISTINCT o.order_id), 0), 2) AS "Average Order Value",
    MAX(p.price) AS "Most Expensive Product Price",
    (SELECT p2.name 
     FROM Products p2
     JOIN Order_Items oi2 ON p2.product_id = oi2.product_id
     JOIN Orders o2 ON oi2.order_id = o2.order_id
     WHERE o2.customer_id = c.customer_id
     ORDER BY p2.price DESC
     LIMIT 1) AS "Most Expensive Product",
    CASE 
        WHEN MAX(p.price) >= 500 THEN 'Premium'
        WHEN MAX(p.price) >= 200 THEN 'Luxury'
    END AS "Tier"
FROM 
    Customers c
    INNER JOIN Orders o ON c.customer_id = o.customer_id
    INNER JOIN Order_Items oi ON o.order_id = oi.order_id
    INNER JOIN Products p ON oi.product_id = p.product_id
GROUP BY 
    c.customer_id, c.first_name, c.last_name, c.city, c.state
HAVING 
    MAX(p.price) >= 200
ORDER BY 
    "Total Spending" DESC;
*/

