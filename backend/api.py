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
