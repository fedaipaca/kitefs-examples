# training

Feature producer for the kitefs-examples demo. Defines KiteFS feature groups, ingests prepared listing and market data, retrieves point-in-time-correct training datasets, trains a price recommendation model, and materializes online features to the feature store.

---

## Generate demo datasets

Before running the KiteFS Getting Started workflow, generate the synthetic Parquet datasets. Run both scripts from the `training/` project root.

### Step 1 — Full year 2025

```bash
uv run python scripts/generate_2025_dataset.py
```

Produces:

| File | Rows | Description |
| ---- | ---- | ----------- |
| `data/listing_features.parquet` | 10,000 | Sold listings, Jan–Dec 2025 |
| `data/town_market_features.parquet` | 72 | Monthly `avg_price_per_sqm` per town (6 towns × 12 months), `event_timestamp` = first day of the following month |

### Step 2 — January 2026

```bash
uv run python scripts/generate_jan2026_dataset.py
```

Produces:

| File | Rows | Description |
| ---- | ---- | ----------- |
| `data/listing_features_jan2026.parquet` | 1,000 | Sold listings, January 2026 |
| `data/town_market_jan2026.parquet` | 6 | `avg_price_per_sqm` per town for January 2026, `event_timestamp` = `2026-02-01 00:00:00 UTC` |

Both scripts are deterministic (fixed random seed) and safe to re-run — they overwrite existing files. `listing_id` values in the January 2026 dataset start at `20001` to avoid collisions with the 2025 dataset when both are ingested into the same feature store.

The market aggregates in each dataset are derived from the generated listing prices, so the numbers are internally consistent and match the SQL-based preparation pattern described in the Getting Started guide (section 1.4).