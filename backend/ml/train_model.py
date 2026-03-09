import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import os

# ---------------- LOAD DATASET ----------------
data_path = "../../data/code_quality_dataset.csv"
df = pd.read_csv(data_path)

# Expected feature columns (Option B)
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
y = df["label"].astype(int)  # Ensure binary labels

# ---------------- TRAIN / TEST SPLIT ----------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ---------------- MODEL PIPELINE ----------------
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        solver="liblinear"
    ))
])

# ---------------- TRAIN ----------------
pipeline.fit(X_train, y_train)

# ---------------- EVALUATE ----------------
y_pred = pipeline.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))

# ---------------- SAVE MODEL ----------------
os.makedirs("../../model", exist_ok=True)
model_path = "../../model/code_quality_model.pkl"
joblib.dump(pipeline, model_path)

print(f"Model saved at: {model_path}")