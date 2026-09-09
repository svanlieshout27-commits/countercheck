"""
CounterCheck API
A FastAPI service that scores e-commerce listings for counterfeit risk
and uses Claude to explain the score in plain language.
"""

import os
import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from anthropic import Anthropic

from features import extract_features

load_dotenv()

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise RuntimeError("CLAUDE_API_KEY not found. Add it to backend/.env")

CLAUDE_MODEL = "claude-opus-4-1-20250805"
claude_client = Anthropic(api_key=CLAUDE_API_KEY)

try:
    clf = joblib.load("model.joblib")
except FileNotFoundError:
    raise RuntimeError("model.joblib not found. Run `python train.py` first.")

app = FastAPI(
    title="CounterCheck API",
    description="Scores e-commerce listings for counterfeit risk and explains why.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Listing(BaseModel):
    title: str = Field(..., example="R0LEX Submariner GENUINE 100% authentic")
    brand: str = Field(..., example="Rolex")
    price: float = Field(..., example=199.0)
    description: str = Field(
        ...,
        example="100% authentic genuine real luxury Swiss timepiece. AAA quality.",
    )

class ScoreResponse(BaseModel):
    listing: Listing
    risk_score: float
    label: str
    explanation: str

def score_listing(listing: Listing) -> tuple[float, str]:
    """Run the trained classifier and return (suspect probability, label)."""
    row = listing.model_dump()
    features = extract_features(row)
    X = pd.DataFrame([features])
    proba = clf.predict_proba(X)[0]
    suspect_proba = float(proba[1])
    label = "suspect" if suspect_proba >= 0.5 else "legit"
    return suspect_proba, label

def explain_with_claude(listing: Listing, score: float, label: str) -> str:
    """Ask Claude to explain the classification in 2-3 sentences."""
    prompt = (
        f"A counterfeit-detection classifier scored the listing below.\n\n"
        f"Title: {listing.title}\n"
        f"Brand: {listing.brand}\n"
        f"Price: ${listing.price}\n"
        f"Description: {listing.description}\n\n"
        f"Classifier output: {label} (suspect probability {score:.2f})\n\n"
        f"In 2-3 short sentences, explain why this listing was flagged as "
        f"{label}. Cite specific signals from the listing (brand spelling, "
        f"price-vs-brand mismatch, suspicious phrases, etc). Be concrete and "
        f"professional — this output is read by brand-protection analysts."
    )

    try:
        response = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=200,
            temperature=0.3,
            system=(
                "You are a senior brand-protection analyst. You explain "
                "counterfeit-detection results in plain, professional "
                "English. Cite specific signals. Never fabricate facts."
            ),
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"(Explanation unavailable: {e})"

@app.get("/")
def root():
    return {
        "name": "CounterCheck API",
        "model": CLAUDE_MODEL,
        "classifier": "logistic regression with class_weight='balanced'",
        "endpoints": ["/score", "/docs"],
    }

@app.post("/score", response_model=ScoreResponse)
def score(listing: Listing):
    try:
        risk_score, label = score_listing(listing)
        explanation = explain_with_claude(listing, risk_score, label)
        return ScoreResponse(
            listing=listing,
            risk_score=round(risk_score, 3),
            label=label,
            explanation=explanation,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
