# CounterCheck

> AI-powered counterfeit listing detector. Combines text-feature classification with LLM reasoning to flag suspect marketplace listings.

**Built by:** Sebastiaan van Lieshout — 6+ years in brand protection at Amazon, processing 1,000+ counterfeit cases monthly.

---

## Status

🚧 **Under active construction** — initial version targeting end of weekend (build log on the `dev` branch).

## What this will be

A web tool where you paste a product listing (title, brand, price, description) and get back:

- A risk score from 0 to 100
- Three flagged signals (price anomalies, suspect phrasing, brand-product mismatches, etc.)
- A plain-English explanation written by an LLM
- A recommended action: **CLEAR / REVIEW / ESCALATE**

## Why

Manual counterfeit review is slow and inconsistent. At scale, human reviewers fatigue and miss patterns. CounterCheck demonstrates how a hybrid ML + LLM system can pre-triage listings so human reviewers focus only on edge cases.

## Architecture (planned)

- **Frontend:** Next.js 16 + Tailwind, deployed on Vercel
- **Backend:** FastAPI + scikit-learn, deployed on Render
- **LLM:** Claude Sonnet 4.5 via Anthropic API (or Groq + Llama 3.3-70B as a fallback)
- **Data:** ~1,000 marketplace listings, hand-labeled subset by domain expert

## Repo layout

```
/backend    Python ML service (FastAPI + scikit-learn classifier)
/frontend   Next.js UI (deployed to Vercel)
/data       Dataset and labels (gitignored where appropriate)
```

## Roadmap

- [ ] Weekend 1: Baseline classifier + Claude explanation layer + live demo
- [ ] Weekend 2: TF-IDF features, gradient boosting, expand to 2–3 product categories
- [ ] Weekend 3: Multimodal — add product-image analysis via Claude vision
- [ ] Weekend 4–5: Polish, write the case-study blog post

## License

MIT — full text added on first release.

---

*This README will be replaced with the real one (live demo link, F1 metrics, screenshots, and run-locally instructions) once the first version ships.*
