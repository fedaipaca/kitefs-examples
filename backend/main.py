import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from kitefs import FeatureStore

load_dotenv()

FEATURE_COLUMNS = [
    "net_area",
    "number_of_rooms",
    "build_year",
    "town_market_features_avg_price_per_sqm",
]

model = joblib.load("model.pkl")
store = FeatureStore()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


class PriceRequest(BaseModel):
    town_id: int
    net_area: int
    number_of_rooms: int
    build_year: int


@app.post("/recommend-price")
def recommend_price(request: PriceRequest) -> dict[str, float]:
    market = store.get_online_features(
        from_="town_market_features",
        select=["avg_price_per_sqm"],
        where={"town_id": {"eq": request.town_id}},
    )

    if not market:
        raise HTTPException(
            status_code=404,
            detail=f"No market data available for town_id={request.town_id}.",
        )

    print(market)

    feature_row = pd.DataFrame([
        {
            "net_area": request.net_area,
            "number_of_rooms": request.number_of_rooms,
            "build_year": request.build_year,
            "town_market_features_avg_price_per_sqm": market["avg_price_per_sqm"],
        }
    ])[FEATURE_COLUMNS]

    predicted_price = float(model.predict(feature_row)[0])
    return {"recommended_price": round(predicted_price, 2)}

