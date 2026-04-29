from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import joblib
import pandas as pd
from features import extract_features

app = FastAPI()

# Allow your frontend to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this later
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load("model.joblib")

class Listing(BaseModel):
    title: str
    description: str = ""
    brand: Optional[str] = None
    price: Optional[float] = None

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/score")
def score(listing: Listing):
    feat_dict = extract_features(listing.model_dump())
    X = pd.DataFrame([feat_dict])
    risk_score = int(model.predict_proba(X)[0][1] * 100)
    flagged = [k for k, v in feat_dict.items() if v > 0]
    return {
        "risk_score": risk_score,
        "flagged_signals": flagged[:3],
        "raw_features": feat_dict,
    }