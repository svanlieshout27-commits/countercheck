import json
import csv
import os

LISTINGS_PATH = "../data/listings.jsonl"
LABELS_PATH = "../data/labels.csv"

# Load existing labels (so you can resume if you stop)
existing = {}
if os.path.exists(LABELS_PATH):
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing[int(row["listing_id"])] = int(row["label"])

# Load listings
listings = []
with open(LISTINGS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        listings.append(json.loads(line))

# Label until we hit 100
labels = dict(existing)
for listing in listings:
    if len(labels) >= 100:
        break
    if listing["listing_id"] in labels:
        continue

    print("\n" + "=" * 70)
    print(f"#{listing['listing_id']}  ({len(labels)}/100 labelled)")
    print(f"Title: {listing.get('title', '')[:120]}")
    print(f"Brand: {listing.get('store', listing.get('brand', 'unknown'))}")
    print(f"Price: {listing.get('price', 'unknown')}")
    desc = (listing.get('description') or [''])[0] if isinstance(listing.get('description'), list) else listing.get('description', '')
    print(f"Description: {str(desc)[:300]}")
    print()

    while True:
        ans = input("Label? [0=legit / 1=suspect / s=skip / q=quit] > ").strip().lower()
        if ans in ("0", "1"):
            labels[listing["listing_id"]] = int(ans)
            break
        if ans == "s":
            break
        if ans == "q":
            print("Saving and quitting...")
            break
    if ans == "q":
        break

# Save
with open(LABELS_PATH, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["listing_id", "label"])
    for lid, lbl in labels.items():
        writer.writerow([lid, lbl])

print(f"\nSaved {len(labels)} labels to {LABELS_PATH}")