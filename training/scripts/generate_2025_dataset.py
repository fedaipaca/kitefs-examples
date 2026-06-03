"""
Generate synthetic 2025 demo datasets for the KiteFS Getting Started guide.

Produces two Parquet files under data/:
  data/listing_features.parquet       — 10,000 sold listings, Jan–Dec 2025
  data/town_market_features.parquet   — monthly avg_price_per_sqm per town,
                                        Jan–Dec 2025 (72 rows, 6 towns × 12 months)

Market aggregates are derived from the generated listing prices so the numbers
are internally consistent.  event_timestamp is set to the first day of the
FOLLOWING month (e.g. January aggregate → 2025-02-01) matching the leakage-
prevention pattern described in the Getting Started guide section 1.4.

Run from the training project root:
    uv run python scripts/generate_2025_dataset.py
"""

from __future__ import annotations

import calendar
import random
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

SEED = 42
N_LISTINGS = 10_000
LISTING_ID_START = 1001

# Anchor prices used only by the random generator below; not stored as a feature.
TOWNS = {
    1: {"name": "Kadikoy", "city": "Istanbul", "base_price_per_sqm": 30_000},
    2: {"name": "Besiktas", "city": "Istanbul", "base_price_per_sqm": 31_500},
    3: {"name": "Tuzla", "city": "Istanbul", "base_price_per_sqm": 22_000},
    4: {"name": "Cankaya", "city": "Ankara", "base_price_per_sqm": 21_000},
    5: {"name": "Kecioren", "city": "Ankara", "base_price_per_sqm": 17_000},
    6: {"name": "Mamak", "city": "Ankara", "base_price_per_sqm": 13_000},
}

# Slight upward monthly drift applied cumulatively: month 1 = +0%, month 12 = +~5.5%
MONTHLY_DRIFT = 0.005  # 0.5% per month

# Rooms-to-area mapping: (min_area, max_area)
ROOMS_AREA = {
    1: (40, 70),
    2: (65, 105),
    3: (95, 150),
    4: (140, 200),
    5: (180, 250),
}


def _month_multiplier(month: int) -> float:
    """Cumulative price drift for a given month (1-based)."""
    return 1.0 + MONTHLY_DRIFT * (month - 1)


def _random_sold_at(rng: random.Random, year: int, month: int) -> datetime:
    """Pick a random UTC datetime within the given year/month."""
    _, last_day = calendar.monthrange(year, month)
    day = rng.randint(1, last_day)
    hour = rng.randint(8, 19)
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)


def generate_listing_features(rng: random.Random) -> list[dict]:
    town_ids = list(TOWNS.keys())

    rows = []
    for i in range(N_LISTINGS):
        listing_id = LISTING_ID_START + i
        town_id = rng.choice(town_ids)
        # Pick a month at random across the year.
        month = rng.randint(1, 12)

        number_of_rooms = rng.choices([1, 2, 3, 4, 5], weights=[5, 30, 40, 20, 5])[0]
        min_area, max_area = ROOMS_AREA[number_of_rooms]
        net_area = rng.randint(min_area, max_area)

        build_year = rng.randint(1980, 2025)

        base = TOWNS[town_id]["base_price_per_sqm"]
        drift = _month_multiplier(month)
        # ±10% per-listing noise
        price_per_sqm = base * drift * rng.uniform(0.90, 1.10)
        sold_price = round(net_area * price_per_sqm, 2)

        sold_at = _random_sold_at(rng, 2025, month)

        rows.append(
            {
                "listing_id": listing_id,
                "town_id": town_id,
                "net_area": net_area,
                "number_of_rooms": number_of_rooms,
                "build_year": build_year,
                "sold_price": sold_price,
                "sold_at": sold_at,
            }
        )

    return rows


def generate_town_market_features(listings_df: pd.DataFrame) -> list[dict]:
    """Derive monthly avg_price_per_sqm per town from the generated listings.

    event_timestamp = first day of the NEXT month (leakage-prevention convention).
    """
    listings_df = listings_df.copy()
    listings_df["month"] = listings_df["sold_at"].dt.month
    listings_df["price_per_sqm"] = listings_df["sold_price"] / listings_df["net_area"]

    agg = (
        listings_df.groupby(["town_id", "month"])["price_per_sqm"]
        .mean()
        .reset_index()
        .rename(columns={"price_per_sqm": "avg_price_per_sqm"})
    )

    rows = []
    for _, row in agg.iterrows():
        month = int(row["month"])
        next_month = month + 1
        next_year = 2025
        if next_month > 12:
            next_month = 1
            next_year = 2026
        event_timestamp = datetime(next_year, next_month, 1, 0, 0, 0, tzinfo=timezone.utc)
        rows.append(
            {
                "town_id": int(row["town_id"]),
                "avg_price_per_sqm": round(float(row["avg_price_per_sqm"]), 2),
                "event_timestamp": event_timestamp,
            }
        )

    return sorted(rows, key=lambda r: (r["event_timestamp"], r["town_id"]))


def main() -> None:
    rng = random.Random(SEED)

    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Generating listing_features (2025)…")
    listing_rows = generate_listing_features(rng)
    listings_df = pd.DataFrame(listing_rows)
    listings_df["sold_at"] = pd.to_datetime(listings_df["sold_at"], utc=True)

    listing_path = out_dir / "listing_features.parquet"
    listings_df.to_parquet(listing_path, index=False)
    print(f"  Written {len(listings_df):,} rows → {listing_path}")

    print("Generating town_market_features (2025)…")
    market_rows = generate_town_market_features(listings_df)
    market_df = pd.DataFrame(market_rows)
    market_df["event_timestamp"] = pd.to_datetime(market_df["event_timestamp"], utc=True)

    market_path = out_dir / "town_market_features.parquet"
    market_df.to_parquet(market_path, index=False)
    print(f"  Written {len(market_df):,} rows → {market_path}")

    print("\nSample listing_features:")
    print(listings_df.head(3).to_string(index=False))
    print("\nSample town_market_features:")
    print(market_df.head(6).to_string(index=False))


if __name__ == "__main__":
    main()
