"""
Run sentiment analysis on review_content and compare it against the
star rating to flag mismatches (e.g. high rating but negative-sounding text).
Input:  amazon_clean.csv
Output: amazon_with_sentiment.csv
"""
import pandas as pd
from textblob import TextBlob

IN_PATH = "data/amazon_clean.csv"
OUT_PATH = "data/amazon_with_sentiment.csv"


def sentiment_label(polarity: float) -> str:
    if polarity > 0.1:
        return "Positive"
    if polarity < -0.1:
        return "Negative"
    return "Neutral"


def main() -> None:
    df = pd.read_csv(IN_PATH)
    df["review_content"] = df["review_content"].fillna("")

    polarity = df["review_content"].apply(lambda t: TextBlob(t).sentiment.polarity)
    df["sentiment_score"] = polarity.round(3)
    df["sentiment_label"] = polarity.apply(sentiment_label)

    # Mismatch flag: high star rating (>=4) but negative text sentiment, or vice versa
    df["rating_sentiment_mismatch"] = (
        ((df["rating"] >= 4.0) & (df["sentiment_label"] == "Negative"))
        | ((df["rating"] <= 2.5) & (df["sentiment_label"] == "Positive"))
    )

    df.to_csv(OUT_PATH, index=False)

    print(f"Rows processed: {len(df)}")
    print(df["sentiment_label"].value_counts())
    print(f"Rating/sentiment mismatches: {df['rating_sentiment_mismatch'].sum()}")
    print(f"Saved -> {OUT_PATH}")


if __name__ == "__main__":
    main()
