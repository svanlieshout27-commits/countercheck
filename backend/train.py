import json
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score
import joblib
from features import extract_features

# Load
labels = pd.read_csv("../data/labels.csv")
listings = []
with open("../data/listings.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        listings.append(json.loads(line))
listings_df = pd.DataFrame(listings)

# Merge labels with listings
df = listings_df.merge(labels, on="listing_id")
print(f"Labelled rows: {len(df)}")
print(df["label"].value_counts())

# Extract features into a DataFrame
X = pd.DataFrame([extract_features(row) for _, row in df.iterrows()])
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train
clf = LogisticRegression(max_iter=1000, class_weight="balanced")
clf.fit(X_train, y_train)

# Evaluate
preds = clf.predict(X_test)
print("\n--- Results ---")
print(classification_report(y_test, preds))
print(f"F1 score: {f1_score(y_test, preds):.3f}")

# Save the model
joblib.dump(clf, "model.joblib")
print("Saved model.joblib")