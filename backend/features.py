import re
from typing import Dict, Any

SUSPECT_PHRASES = [
    "100% original", "100% authentic", "100% genuine",
    "brand new with tags", "factory sealed", "bnwt",
    "high quality replica", "aaaa+", "1:1 mirror",
]

# Common counterfeit-seller misspellings / number-letter swaps
BRAND_REGEXES = [
    re.compile(r"\b(r0lex|rolexx|rolax)\b", re.I),
    re.compile(r"\b(nikee|niike|niqe)\b", re.I),
    re.compile(r"\b(adidos|adiddas|addidas)\b", re.I),
    re.compile(r"\b(loui[s5] vu1tton|louis vu1tton|lv\d+)\b", re.I),
    re.compile(r"\b(gucc1|guccii)\b", re.I),
]

def extract_features(listing: Dict[str, Any]) -> Dict[str, float]:
    title = str(listing.get("title", "") or "")
    desc_raw = listing.get("description", "") or ""
    if isinstance(desc_raw, list):
        desc_raw = " ".join(str(d) for d in desc_raw)
    desc = str(desc_raw)
    text = (title + " " + desc).lower()

    # Try to read price as float
    try:
        price = float(listing.get("price", 0) or 0)
    except (ValueError, TypeError):
        price = 0.0

    # 1. Suspect phrase count
    phrase_hits = sum(1 for p in SUSPECT_PHRASES if p in text)

    # 2. Brand misspelling count
    brand_hits = sum(1 for r in BRAND_REGEXES if r.search(text))

    # 3. Suspiciously low price (under €30 — naive but works for watches)
    low_price = 1.0 if 0 < price < 30 else 0.0

    # 4. ALL CAPS shouting in title
    title_caps_ratio = (
        sum(1 for c in title if c.isupper()) / max(len(title), 1)
    )
    shouting = 1.0 if title_caps_ratio > 0.5 else 0.0

    # 5. Description word count (very short = suspicious for high-value items)
    word_count = len(desc.split())
    too_short = 1.0 if word_count < 10 else 0.0

    # 6. Excessive exclamation marks
    excl_ratio = text.count("!") / max(len(text), 1)
    excl_spam = 1.0 if excl_ratio > 0.01 else 0.0

    return {
        "phrase_hits": float(phrase_hits),
        "brand_misspellings": float(brand_hits),
        "low_price": low_price,
        "shouting_title": shouting,
        "too_short_desc": too_short,
        "excl_spam": excl_spam,
    }