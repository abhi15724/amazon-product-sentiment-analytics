"""
Aggregate the cleaned/sentiment-scored dataset into the JSON structure
consumed by dashboard.html. Re-run this if the underlying data changes,
then re-embed the output into dashboard.html's `const DATA = ...` line.
"""
import pandas as pd
import json

IN_PATH = "data/amazon_with_sentiment.csv"
OUT_PATH = "dashboard/dashboard_data.json"


def band(price: float) -> str:
    if price < 500:
        return "<500"
    if price < 1500:
        return "500-1499"
    if price < 5000:
        return "1500-4999"
    return "5000+"


def main() -> None:
    df = pd.read_csv(IN_PATH)

    kpis = {
        "total_products": int(len(df)),
        "avg_rating": round(df["rating"].mean(), 2),
        "avg_discount": round(df["discount_percentage"].mean(), 1),
        "total_reviews": int(df["rating_count"].sum()),
    }

    cat = (
        df.groupby("main_category")
        .agg(
            product_count=("product_id", "count"),
            avg_price=("discounted_price", "mean"),
            avg_discount=("discount_percentage", "mean"),
            avg_rating=("rating", "mean"),
            total_reviews=("rating_count", "sum"),
        )
        .reset_index()
        .sort_values("total_reviews", ascending=False)
    )
    cat["avg_price"] = cat["avg_price"].round(0)
    cat["avg_discount"] = cat["avg_discount"].round(1)
    cat["avg_rating"] = cat["avg_rating"].round(2)

    scatter = df[["discount_percentage", "rating", "main_category", "product_name"]].dropna().rename(
        columns={"discount_percentage": "x", "rating": "y", "main_category": "cat", "product_name": "name"}
    )
    scatter["name"] = scatter["name"].str.slice(0, 60)

    df["price_band"] = df["discounted_price"].apply(band)
    band_order = ["<500", "500-1499", "1500-4999", "5000+"]
    pb = (
        df.groupby("price_band")
        .agg(count=("product_id", "count"), avg_rating=("rating", "mean"))
        .reindex(band_order)
        .reset_index()
    )
    pb["avg_rating"] = pb["avg_rating"].round(2)

    sent_overall = df["sentiment_label"].value_counts().to_dict()

    sent_cat = df.groupby(["main_category", "sentiment_label"]).size().unstack(fill_value=0)
    sent_cat = sent_cat.reindex(columns=["Positive", "Neutral", "Negative"], fill_value=0)
    sentiment_by_category = [
        {"category": idx, "Positive": int(row["Positive"]), "Neutral": int(row["Neutral"]), "Negative": int(row["Negative"])}
        for idx, row in sent_cat.iterrows()
    ]

    mismatch = df[df["rating_sentiment_mismatch"] == True][
        ["product_name", "main_category", "rating", "sentiment_label", "sentiment_score"]
    ].copy()
    mismatch["product_name"] = mismatch["product_name"].str.slice(0, 80)

    redflag = df[(df["discount_percentage"] > 60) & (df["rating"] < 3.5)][
        ["product_name", "main_category", "discount_percentage", "rating", "rating_count"]
    ].sort_values("discount_percentage", ascending=False).copy()
    redflag["product_name"] = redflag["product_name"].str.slice(0, 80)

    output = {
        "kpis": kpis,
        "category": cat.to_dict(orient="records"),
        "scatter": scatter.to_dict(orient="records"),
        "price_bands": pb.to_dict(orient="records"),
        "sentiment_overall": sent_overall,
        "sentiment_by_category": sentiment_by_category,
        "mismatch": mismatch.to_dict(orient="records"),
        "redflag": redflag.to_dict(orient="records"),
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f)

    print(f"Saved -> {OUT_PATH}")


if __name__ == "__main__":
    main()
