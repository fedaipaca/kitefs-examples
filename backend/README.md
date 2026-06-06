# backend

Feature consumer for the kitefs-examples demo. A FastAPI service that reads the latest market features from the KiteFS online store and combines them with listing inputs to return a real-time price recommendation.

## Setup

1. Copy `.env.example` to `.env` and fill in your values:

   ```bash
   cp .env.example .env
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Start the server:

   ```bash
   uv run fastapi dev main.py
   ```

   The API is available at `http://localhost:8000`.

## Endpoint

```
POST /recommend-price
Content-Type: application/json

{
  "town_id": 1,
  "net_area": 105,
  "number_of_rooms": 3,
  "build_year": 2000
}
```

Returns:

```json
{ "recommended_price": 3120000.0 }
```

Returns HTTP 404 when no online feature data exists for the given `town_id`.