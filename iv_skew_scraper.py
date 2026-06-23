"""Fetch daily 30-Day Implied Volatility Skew for a ticker from AlphaQuery and save to CSV."""

import argparse
import csv
from pathlib import Path

import requests

ALPHAQUERY_CHART_URL = "https://www.alphaquery.com/data/option-statistic-chart"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_iv_skew(ticker: str, per_type: str = "30-Day") -> list[dict]:
    """Return a list of {"date": "YYYY-MM-DD", "iv_skew": float} records for ticker."""
    response = requests.get(
        ALPHAQUERY_CHART_URL,
        params={"ticker": ticker, "perType": per_type, "identifier": "iv-mean-skew"},
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return [{"date": point["x"][:10], "iv_skew": point["value"]} for point in data]


def save_csv(records: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "iv_skew"])
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker", help="Stock ticker, e.g. AAPL")
    parser.add_argument(
        "--per-type",
        default="30-Day",
        choices=[
            "10-Day", "20-Day", "30-Day", "60-Day",
            "90-Day", "120-Day", "150-Day", "180-Day",
        ],
        help="IV lookback window (default: 30-Day)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output CSV path (default: data/<ticker>_iv_skew_<per-type>.csv)",
    )
    args = parser.parse_args()

    records = fetch_iv_skew(args.ticker, args.per_type)

    output_path = Path(
        args.output
        or f"data/{args.ticker.upper()}_iv_skew_{args.per_type}.csv"
    )
    save_csv(records, output_path)
    print(f"Saved {len(records)} rows to {output_path}")


if __name__ == "__main__":
    main()
