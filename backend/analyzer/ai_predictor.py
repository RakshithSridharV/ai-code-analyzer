import joblib
import os
import pandas as pd

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../model/code_quality_model.pkl"
)

model = joblib.load(MODEL_PATH)

def predict_code_quality(features):
    """
    Features MUST be:
    [loop_depth, is_recursive, uses_extra_memory, time_penalty, space_penalty]
    """

    df = pd.DataFrame([features], columns=[
        "loop_depth",
        "is_recursive",
        "uses_extra_memory",
        "time_penalty",
        "space_penalty"
    ])

    prediction = model.predict(df)[0]
    return "Inefficient" if prediction == 1 else "Efficient"