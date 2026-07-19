-- =====================================================================
-- Amazon Product & Customer Sentiment Analytics — SQL Analysis Layer
-- Table: products  (loaded via 03_load_to_sqlite.py)
-- =====================================================================

-- 1. Category overview: avg price, avg discount, avg rating, review volume
SELECT
    main_category,
    COUNT(*)                          AS product_count,
    ROUND(AVG(discounted_price), 2)   AS avg_price,
    ROUND(AVG(discount_percentage),1) AS avg_discount_pct,
    ROUND(AVG(rating), 2)             AS avg_rating,
    SUM(rating_count)                 AS total_reviews
FROM products
GROUP BY main_category
ORDER BY total_reviews DESC;


-- 2. Red flags: heavy discount (>60%) but below-average rating (<3.5)
SELECT
    product_name,
    main_category,
    discount_percentage,
    rating,
    rating_count
FROM products
WHERE discount_percentage > 60
  AND rating < 3.5
ORDER BY discount_percentage DESC;


-- 3. Price vs. rating correlation proxy — bucket by price range
SELECT
    CASE
        WHEN discounted_price < 500  THEN '<500'
        WHEN discounted_price < 1500 THEN '500-1499'
        WHEN discounted_price < 5000 THEN '1500-4999'
        ELSE '5000+'
    END AS price_band,
    COUNT(*)               AS product_count,
    ROUND(AVG(rating), 2)  AS avg_rating
FROM products
GROUP BY price_band
ORDER BY MIN(discounted_price);


-- 4. Window function: rank products within each category by review volume
-- (SQLite has no QUALIFY clause, so the rank filter is applied via a subquery)
SELECT * FROM (
    SELECT
        main_category,
        product_name,
        rating,
        rating_count,
        RANK() OVER (
            PARTITION BY main_category
            ORDER BY rating_count DESC
        ) AS review_rank_in_category
    FROM products
) ranked
WHERE review_rank_in_category <= 3
ORDER BY main_category, review_rank_in_category;


-- 5. CTE: most-reviewed vs. highest-rated per category (are they the same product?)
WITH most_reviewed AS (
    SELECT main_category, product_name, rating_count,
           RANK() OVER (PARTITION BY main_category ORDER BY rating_count DESC) AS rnk
    FROM products
),
highest_rated AS (
    SELECT main_category, product_name, rating,
           RANK() OVER (PARTITION BY main_category ORDER BY rating DESC, rating_count DESC) AS rnk
    FROM products
)
SELECT
    mr.main_category,
    mr.product_name AS most_reviewed_product,
    hr.product_name AS highest_rated_product,
    CASE WHEN mr.product_name = hr.product_name THEN 'Same' ELSE 'Different' END AS alignment
FROM most_reviewed mr
JOIN highest_rated hr ON mr.main_category = hr.main_category AND hr.rnk = 1
WHERE mr.rnk = 1;


-- 6. Sentiment vs. star rating mismatch report (uses Python-derived sentiment columns)
SELECT
    product_name,
    main_category,
    rating,
    sentiment_label,
    sentiment_score
FROM products
WHERE rating_sentiment_mismatch = 1
ORDER BY rating DESC;


-- 7. Sentiment distribution by category
SELECT
    main_category,
    sentiment_label,
    COUNT(*) AS num_products
FROM products
GROUP BY main_category, sentiment_label
ORDER BY main_category, sentiment_label;
