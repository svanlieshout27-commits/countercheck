import json
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from features import extract_features

model = joblib.load("model.joblib")
labels = pd.read_csv("../data/labels.csv")
listings = []
with open("../data/listings.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        listings.append(json.loads(line))
listings_df = pd.DataFrame(listings)
df = listings_df.merge(labels, on="listing_id")

X = pd.DataFrame([extract_features(row) for _, row in df.iterrows()])
y = df["label"]
preds = model.predict(X)

print("=== Full-set evaluation ===")
print(classification_report(y, preds))
print("\nConfusion matrix:")
print(confusion_matrix(y, preds))

# Save false positives for review
fps = df[(y == 0) & (preds == 1)].head(10)
fps[["listing_id", "title", "price"]].to_csv("../data/false_positives.csv", index=False)
print(f"\nSaved {len(fps)} false positives for review")