"""
Clean and transform the raw Amazon product dataset.
Input:  amazon.csv (raw)
Output: amazon_clean.csv
"""
import pandas as pd
import re

RAW_PATH = "data/raw_amazon.csv"
OUT_PATH = "data/amazon_clean.csv"


def money_to_float(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace("", "0")
        .astype(float)
    )


def percent_to_float(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
        .replace("", "0")
        .astype(float)
    )


def clean_count(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.replace(",", "", regex=False).str.strip()
    return pd.to_numeric(cleaned, errors="coerce")


def main() -> None:
    df = pd.read_csv(RAW_PATH)

    # --- price / numeric fields ---
    df["discounted_price"] = money_to_float(df["discounted_price"])
    df["actual_price"] = money_to_float(df["actual_price"])
    df["discount_percentage"] = percent_to_float(df["discount_percentage"])
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["rating_count"] = clean_count(df["rating_count"])

    # --- category split (pipe-delimited hierarchy) ---
    cat_split = df["category"].astype(str).str.split("|", expand=True)
    df["main_category"] = cat_split[0]
    df["sub_category"] = cat_split[1] if cat_split.shape[1] > 1 else None

    # --- drop rows with no usable price/rating (can't analyze them) ---
    before = len(df)
    df = df.dropna(subset=["discounted_price", "actual_price", "rating"])
    dropped = before - len(df)

    # --- derived metric: computed discount check (sanity vs listed %) ---
    df["computed_discount_pct"] = (
        (df["actual_price"] - df["discounted_price"]) / df["actual_price"] * 100
    ).round(1)

    keep_cols = [
        "product_id", "product_name", "main_category", "sub_category", "category",
        "discounted_price", "actual_price", "discount_percentage",
        "computed_discount_pct", "rating", "rating_count",
        "about_product", "review_id", "review_title", "review_content",
        "user_id", "user_name", "img_link", "product_link",
    ]
    df = df[keep_cols]

    df.to_csv(OUT_PATH, index=False)
    print(f"Rows in:  {before}")
    print(f"Rows dropped (bad price/rating): {dropped}")
    print(f"Rows out: {len(df)}")
    print(f"Saved -> {OUT_PATH}")


if __name__ == "__main__":
    main()
