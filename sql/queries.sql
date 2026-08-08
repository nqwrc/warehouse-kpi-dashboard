-- KPI queries for the warehouse database.
-- Written to be readable: each query answers one operational question.
-- Run them with: sqlite3 warehouse.db < sql/queries.sql   (or one by one)

---------------------------------------------------------------------------
-- Q1. Overall picking error rate — are we below the 1% company target?
-- error rate = lines with an error / total picked lines
---------------------------------------------------------------------------
SELECT
    COUNT(*)                                            AS total_lines,
    SUM(CASE WHEN error_type <> '' THEN 1 ELSE 0 END)   AS error_lines,
    ROUND(100.0 * SUM(CASE WHEN error_type <> '' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                AS error_rate_pct
FROM order_lines;

---------------------------------------------------------------------------
-- Q2. Error rate per picker — who needs coaching, who can mentor?
-- Same calculation as Q1, but grouped by operator.
---------------------------------------------------------------------------
SELECT
    picker_id,
    COUNT(*)                                            AS lines_picked,
    SUM(CASE WHEN error_type <> '' THEN 1 ELSE 0 END)   AS errors,
    ROUND(100.0 * SUM(CASE WHEN error_type <> '' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                AS error_rate_pct
FROM order_lines
GROUP BY picker_id
ORDER BY error_rate_pct DESC;

---------------------------------------------------------------------------
-- Q3. Weekly error trend — is the situation improving or degrading?
-- strftime('%Y-%W') turns each date into its year-week bucket.
---------------------------------------------------------------------------
SELECT
    strftime('%Y-%W', pick_date)                        AS year_week,
    COUNT(*)                                            AS lines,
    ROUND(100.0 * SUM(CASE WHEN error_type <> '' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                AS error_rate_pct
FROM order_lines
GROUP BY year_week
ORDER BY year_week;

---------------------------------------------------------------------------
-- Q4. What kind of errors happen most? (Pareto view)
---------------------------------------------------------------------------
SELECT
    error_type,
    COUNT(*)                                            AS occurrences
FROM order_lines
WHERE error_type <> ''
GROUP BY error_type
ORDER BY occurrences DESC;

---------------------------------------------------------------------------
-- Q5. Picking volume by category — where does the work actually go?
-- JOIN connects each picked line to its product record.
---------------------------------------------------------------------------
SELECT
    p.category,
    COUNT(*)                                            AS lines,
    SUM(l.qty_ordered)                                  AS units
FROM order_lines AS l
JOIN products    AS p ON p.sku = l.sku
GROUP BY p.category
ORDER BY units DESC;

---------------------------------------------------------------------------
-- Q6. Expiry risk: lots that expire within 30 days of the last activity date.
-- julianday() lets SQLite compute the difference between two dates in days.
-- Note: reusing the days_to_expiry alias in WHERE works in SQLite but is not
-- standard SQL — PostgreSQL would need the expression repeated or a subquery.
---------------------------------------------------------------------------
SELECT
    lo.lot_code,
    p.product_name,
    lo.expiry_date,
    CAST(julianday(lo.expiry_date)
         - julianday((SELECT MAX(pick_date) FROM order_lines)) AS INTEGER)
                                                        AS days_to_expiry,
    lo.qty_received
FROM lots     AS lo
JOIN products AS p ON p.sku = lo.sku
WHERE days_to_expiry BETWEEN 0 AND 30
ORDER BY days_to_expiry;
