# Amazon Product & Customer Sentiment Analytics

End-to-end analytics project: raw Amazon India product data → cleaned in **Python** →
analyzed with **SQL** → visualized in an interactive **HTML dashboard** (and set up
for **Power BI**).

**[▶ Open the live dashboard](dashboard/dashboard.html)** — self-contained, no server needed, works offline.

## Dataset
1,464 Amazon India product listings across 9 categories, including pricing, ratings,
and customer review text.

## Repository structure
```
.
├── data/
│   ├── raw_amazon.csv            # original source data
│   ├── amazon_with_sentiment.csv # final cleaned + sentiment-scored dataset
│   └── amazon.db                 # SQLite database (table: products) — connect Power BI here
├── src/
│   ├── 01_clean_data.py          # currency/percent parsing, category split, type fixes
│   ├── 02_sentiment_analysis.py  # TextBlob sentiment scoring + rating/sentiment mismatch flag
│   ├── 03_load_to_sqlite.py      # loads cleaned data into data/amazon.db
│   └── 05_build_dashboard_data.py# aggregates data into the JSON the dashboard embeds
├── sql/
│   └── 04_analysis_queries.sql   # 7 analysis queries (KPIs, red flags, window fns, CTEs)
├── dashboard/
│   └── dashboard.html            # standalone interactive dashboard (Chart.js, embedded data)
└── requirements.txt
```

## Pipeline

| Step | Script | What it does |
|---|---|---|
| 1 | `src/01_clean_data.py` | Strips currency symbols/commas, converts price & rating fields to numeric, splits the pipe-delimited category hierarchy into `main_category` / `sub_category`, drops unusable rows |
| 2 | `src/02_sentiment_analysis.py` | Runs TextBlob sentiment scoring on review text; flags products where the star rating and review sentiment disagree |
| 3 | `src/03_load_to_sqlite.py` | Loads the cleaned, scored dataset into `data/amazon.db` for querying and for Power BI to connect to |
| 4 | `sql/04_analysis_queries.sql` | 7 analysis queries: category KPIs, discount/rating red flags, price-band rating trends, window-function ranking, CTE comparisons, sentiment mismatch report |
| 5 | `src/05_build_dashboard_data.py` | Aggregates the final dataset into the JSON structure the dashboard embeds |
| 6 | Power BI | Connect to `data/amazon.db` (or `data/amazon_with_sentiment.csv`) and build the dashboard below |

## Key findings (from the SQL layer)
- Electronics and Computers&Accessories dominate both product count and total review volume
- A handful of products combine >60% discount with sub-3.5 ratings — worth flagging for quality review
- 9 products show a sentiment vs. star-rating mismatch — reviews that read negative despite a high star rating, useful for catching fake/rushed 5-star reviews

## HTML dashboard
`dashboard/dashboard.html` is a standalone, self-contained interactive dashboard —
no server, no installs, works fully offline (Chart.js is embedded inline). It's laid
out as four tabs, mirroring how the Power BI file is organized:
1. **Overview** — KPI cards, category breakdown, sentiment mix
2. **Pricing & Discounts** — discount % vs. rating scatter (filterable by category), rating by price band
3. **Sentiment** — sentiment by category, overall sentiment mix
4. **Flagged Products** — the two red-flag tables from the SQL layer

## Power BI dashboard
Connect Power BI Desktop to `data/amazon.db` (Get Data → ODBC/SQLite) or import
`data/amazon_with_sentiment.csv` directly, then build the same four pages described
above.

## How to reproduce
```bash
pip install -r requirements.txt
python src/01_clean_data.py
python src/02_sentiment_analysis.py
python src/03_load_to_sqlite.py
python src/05_build_dashboard_data.py
sqlite3 data/amazon.db < sql/04_analysis_queries.sql   # or run queries individually
```

## Tech stack
Python (pandas, TextBlob) · SQL (SQLite: window functions, CTEs) · Power BI · HTML/CSS/JS (Chart.js)
