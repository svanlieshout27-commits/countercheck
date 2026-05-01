# CounterCheck

**Hybrid ML + LLM counterfeit listing detector.** A scikit-learn classifier scores product listings for counterfeit risk; Llama 3.3-70B explains *why* in plain English.

**Live demo:** [<LIVE_URL>](https://countercheck-eight.vercel.app/)
**Repo:** https://github.com/svanlieshout27-commits/countercheck

---

## What it does

Paste a product listing (title, brand, price, description) and CounterCheck returns:

- A **risk score** between 0.0 and 1.0
- A **label**: `legit` or `suspect`
- A **plain-English explanation** of what drove the decision

The model was trained on 100 hand-labeled synthetic listings covering common counterfeit watch patterns (Casio, Rolex, etc.) and their authentic counterparts.

## Architecture

The request flow is intentionally simple:

1. User submits a listing through the Next.js form, deployed on Vercel.
2. The form POSTs to a FastAPI backend deployed on Render.
3. The backend extracts features and runs a scikit-learn LogisticRegression classifier to produce a risk score.
4. The score and the original listing are passed to Groq (Llama 3.3-70B-versatile) with a constrained prompt asking for a 2–3 sentence explanation.
5. The backend returns `{ risk_score, label, explanation }` as JSON; the frontend renders it.

The LLM never overrides the classifier — it only interprets it. The classifier is the source of truth; the LLM is the presentation layer.

## Results

| Metric | Value |
|---|---|
| F1 score (held-out test set) | **0.91** |
| Precision (suspect class) | **1.00** |
| Recall (suspect class) | 0.83 |
| False positive rate | 0% |

Trained on 80 listings, evaluated on 20. Precision was prioritized over recall: in brand-protection workflows, taking down a legitimate listing carries more reputational and legal cost than missing a counterfeit on the first pass.

## Limitations

This is a portfolio demo, and the gaps are part of the story.

**1. Feature coverage is bounded by the training set.**
The classifier relies on patterns it has seen — leetspeak digit substitution (`R01ex`, `Cas10`), price-vs-brand outliers, and keyword signals (`super clone`, `BNWT`, etc.). Novel substitutions or brand spellings outside the training distribution can slip through. During testing, an `R01ex` variant was initially scored as legit (0.371). A labeling correction and retrain fixed it, but the underlying issue is real: production systems need fuzzy brand matching and active-learning loops, not a static training set.

**2. The LLM explanation can confabulate.**
Llama 3.3-70B is given the classifier's score and the listing, but it can invent plausible-sounding reasons that aren't actually what drove the score. This architecture treats the classifier as ground truth and the LLM as a presentation layer — readers should know the explanation is not a faithful interpretability tool. Real interpretability would require SHAP values or feature-attribution surfaced alongside the LLM text.

**3. Model artifacts are version-coupled.**
The pickled `model.joblib` is tied to the scikit-learn version it was trained with. A version mismatch between local training (1.7+) and Render's installed version (1.5) caused a `'LogisticRegression' object has no attribute 'multi_class'` runtime error in production. The fix was pinning `scikit-learn==1.7.1` in `backend/requirements.txt`. A production system would address this with ONNX export or a CI step that retrains on the deployed version.

## Run locally

### Backend

```
cd backend
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt
python train.py                   # writes model.joblib
uvicorn api:app --reload          # http://localhost:8000
```

Create `backend/.env` with:

```
GROQ_API_KEY=gsk_...
```

### Frontend

```
cd frontend
npm install
echo "BACKEND_URL=http://localhost:8000" > .env.local
npm run dev                       # http://localhost:3000
```

## Tech stack

- **Classifier:** scikit-learn LogisticRegression (`class_weight="balanced"`)
- **LLM:** Llama 3.3-70B-versatile via Groq
- **Backend:** FastAPI + uvicorn, deployed on Render free tier (Python 3.12.7)
- **Frontend:** Next.js 16 (App Router), Tailwind CSS, deployed on Vercel
- **Data:** 100 hand-labeled synthetic listings (`data/listings.jsonl`, `data/labels.csv`)

## Built by

[**Sebastiaan van Lieshout**](https://www.linkedin.com/in/sebastiaan-van-lieshout/) — Brand Protection Specialist at Amazon Barcelona transitioning into AI engineering. CounterCheck bridges real-world IP enforcement context with practical ML systems.
