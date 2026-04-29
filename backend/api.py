"""
CounterCheck API
A FastAPI service that scores e-commerce listings for counterfeit risk
and uses Groq + Llama 3.3-70B to explain the score in plain language.
"""

import os
import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from groq import Groq

from features import extract_features

# ----- Environment -----
load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found. Add it to backend/.env")

GROQ_MODEL = "llama-3.3-70b-versatile"
groq_client = Groq(api_key=GROQ_API_KEY)

# ----- Load trained classifier -----
try:
    clf = joblib.load("model.joblib")
except FileNotFoundError:
    raise RuntimeError("model.joblib not found. Run `python train.py` first.")

# ----- FastAPI app -----
app = FastAPI(
    title="CounterCheck API",
    description="Scores e-commerce listings for counterfeit risk and explains why.",
    version="0.1.0",
)

# CORS — allow the Next.js frontend (and Swagger UI) to call this API.
# Tighten allow_origins to your Vercel domain before going public.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Schemas -----
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

# ----- Helpers -----
def score_listing(listing: Listing) -> tuple[float, str]:
    """Run the trained classifier and return (suspect probability, label)."""
    row = listing.model_dump()
    features = extract_features(row)
    X = pd.DataFrame([features])
    proba = clf.predict_proba(X)[0]
    suspect_proba = float(proba[1])  # class 1 == suspect
    label = "suspect" if suspect_proba >= 0.5 else "legit"
    return suspect_proba, label

def explain_with_groq(listing: Listing, score: float, label: str) -> str:
    """Ask Llama 3.3-70B (via Groq) to explain the classification in 2-3 sentences."""
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
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=200,
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior brand-protection analyst. You explain "
                        "counterfeit-detection results in plain, professional "
                        "English. Cite specific signals. Never fabricate facts."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Explanation unavailable: {e})"

# ----- Endpoints -----
@app.get("/")
def root():
    return {
        "name": "CounterCheck API",
        "model": GROQ_MODEL,
        "classifier": "logistic regression with class_weight='balanced'",
        "endpoints": ["/score", "/docs"],
    }

@app.post("/score", response_model=ScoreResponse)
def score(listing: Listing):
    try:
        risk_score, label = score_listing(listing)
        explanation = explain_with_groq(listing, risk_score, label)
        return ScoreResponse(
            listing=listing,
            risk_score=round(risk_score, 3),
            label=label,
            explanation=explanation,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))