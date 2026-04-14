import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import os

data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "code_quality_dataset.csv")
df = pd.read_csv(data_path)

# Expected feature columns
FEATURE_COLUMNS = [
    "loop_depth",
    "is_recursive",
    "uses_extra_memory",
    "time_penalty",
    "space_penalty"
]

# Validate dataset
missing = set(FEATURE_COLUMNS + ["label"]) - set(df.columns)
if missing:
    raise ValueError(f"Dataset missing columns: {missing}")

X = df[FEATURE_COLUMNS]
y = df["label"].astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        class_weight="balanced",
        random_state=42
    ))
])

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))

model_dir = os.path.join(os.path.dirname(__file__), "..", "..", "model")
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, "code_quality_model.pkl")
joblib.dump(pipeline, model_path)

print(f"Model saved at: {model_path}")

report_path = os.path.join(model_dir, "classification_report.txt")
with open(report_path, "w") as f:
    f.write(classification_report(y_test, y_pred))
print(f"Classification report saved at: {report_path}")