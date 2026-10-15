-- E-commerce Sales & Customer Insights
-- Assumes orders.csv is loaded into a table named orders.
-- Cancelled and returned orders are excluded from recognized revenue.

-- 1. Monthly performance
SELECT
    DATE_TRUNC('MONTH', TO_DATE(order_date)) AS month,
    COUNT(DISTINCT IFF(status = 'Completed', order_id, NULL)) AS completed_orders,
    COUNT(DISTINCT IFF(status = 'Completed', customer_id, NULL)) AS unique_customers,
    SUM(IFF(status = 'Completed', net_revenue, 0)) AS recognized_revenue,
    SUM(IFF(status = 'Completed', estimated_profit, 0)) AS estimated_profit,
    recognized_revenue / NULLIF(completed_orders, 0) AS average_order_value
FROM orders
GROUP BY 1
ORDER BY 1;

-- 2. Category performance
SELECT
    category,
    COUNT(DISTINCT IFF(status = 'Completed', order_id, NULL)) AS completed_orders,
    SUM(IFF(status = 'Completed', net_revenue, 0)) AS recognized_revenue,
    SUM(IFF(status = 'Completed', estimated_profit, 0)) AS estimated_profit
FROM orders
GROUP BY category
ORDER BY recognized_revenue DESC;

-- 3. Order status quality check
SELECT status, COUNT(*) AS order_rows
FROM orders
GROUP BY status
ORDER BY order_rows DESC;

-- 4. Duplicate order ID check (expected result: zero rows)
SELECT order_id, COUNT(*) AS row_count
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- 5. Basic data-quality check
SELECT *
FROM orders
WHERE order_id IS NULL
   OR order_date IS NULL
   OR quantity <= 0
   OR unit_price < 0
   OR discount_pct < 0
   OR discount_pct > 1;
