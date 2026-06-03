"""
Generate synthetic January 2026 demo datasets for the KiteFS Getting Started guide.

Produces two Parquet files under data/:
  data/listing_features_jan2026.parquet  — 1,000 sold listings, January 2026
  data/town_market_jan2026.parquet       — avg_price_per_sqm per town for Jan 2026
                                           (6 rows, one per town)

Market aggregates are derived from the generated listing prices.
event_timestamp is set to 2026-02-01 00:00:00 UTC (first day of February)
matching the leakage-prevention pattern described in the Getting Started
guide section 3.1.

listing_id values start at 20001 to avoid colliding with the 2025 dataset
(IDs 1001–11000) when both are ingested into the same feature store.

Run from the training project root:
    uv run python scripts/generate_jan2026_dataset.py
"""

from __future__ import annotations

import random
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

SEED = 99
N_LISTINGS = 1_000
LISTING_ID_START = 20_001  # non-overlapping with 2025 dataset

# Anchor prices used only by the random generator below; not stored as a feature.
TOWNS = {
    1: {"name": "Kadikoy", "city": "Istanbul", "base_price_per_sqm": 31_500},
    2: {"name": "Besiktas", "city": "Istanbul", "base_price_per_sqm": 33_000},
    3: {"name": "Tuzla", "city": "Istanbul", "base_price_per_sqm": 23_100},
    4: {"name": "Cankaya", "city": "Ankara", "base_price_per_sqm": 22_000},
    5: {"name": "Kecioren", "city": "Ankara", "base_price_per_sqm": 17_800},
    6: {"name": "Mamak", "city": "Ankara", "base_price_per_sqm": 13_700},
}

ROOMS_AREA = {
    1: (40, 70),
    2: (65, 105),
    3: (95, 150),
    4: (140, 200),
    5: (180, 250),
}


def _random_sold_at_jan2026(rng: random.Random) -> datetime:
    day = rng.randint(1, 31)
    hour = rng.randint(8, 19)
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return datetime(2026, 1, day, hour, minute, second, tzinfo=timezone.utc)


def generate_listing_features(rng: random.Random) -> list[dict]:
    town_ids = list(TOWNS.keys())
    rows = []
    for i in range(N_LISTINGS):
        listing_id = LISTING_ID_START + i
        town_id = rng.choice(town_ids)

        number_of_rooms = rng.choices([1, 2, 3, 4, 5], weights=[5, 30, 40, 20, 5])[0]
        min_area, max_area = ROOMS_AREA[number_of_rooms]
        net_area = rng.randint(min_area, max_area)

        build_year = rng.randint(1980, 2025)

        base = TOWNS[town_id]["base_price_per_sqm"]
        price_per_sqm = base * rng.uniform(0.90, 1.10)
        sold_price = round(net_area * price_per_sqm, 2)

        sold_at = _random_sold_at_jan2026(rng)

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
    """Derive avg_price_per_sqm per town from January 2026 listings.

    event_timestamp = 2026-02-01 00:00:00 UTC (leakage-prevention convention).
    """
    listings_df = listings_df.copy()
    listings_df["price_per_sqm"] = listings_df["sold_price"] / listings_df["net_area"]

    agg = (
        listings_df.groupby("town_id")["price_per_sqm"]
        .mean()
        .reset_index()
        .rename(columns={"price_per_sqm": "avg_price_per_sqm"})
    )

    event_timestamp = datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    rows = []
    for _, row in agg.iterrows():
        rows.append(
            {
                "town_id": int(row["town_id"]),
                "avg_price_per_sqm": round(float(row["avg_price_per_sqm"]), 2),
                "event_timestamp": event_timestamp,
            }
        )

    return sorted(rows, key=lambda r: r["town_id"])


def main() -> None:
    rng = random.Random(SEED)

    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Generating listing_features_jan2026…")
    listing_rows = generate_listing_features(rng)
    listings_df = pd.DataFrame(listing_rows)
    listings_df["sold_at"] = pd.to_datetime(listings_df["sold_at"], utc=True)

    listing_path = out_dir / "listing_features_jan2026.parquet"
    listings_df.to_parquet(listing_path, index=False)
    print(f"  Written {len(listings_df):,} rows → {listing_path}")

    print("Generating town_market_jan2026…")
    market_rows = generate_town_market_features(listings_df)
    market_df = pd.DataFrame(market_rows)
    market_df["event_timestamp"] = pd.to_datetime(market_df["event_timestamp"], utc=True)

    market_path = out_dir / "town_market_jan2026.parquet"
    market_df.to_parquet(market_path, index=False)
    print(f"  Written {len(market_df):,} rows → {market_path}")

    print("\nSample listing_features_jan2026:")
    print(listings_df.head(3).to_string(index=False))
    print("\ntown_market_jan2026 (all rows):")
    print(market_df.to_string(index=False))


if __name__ == "__main__":
    main()
