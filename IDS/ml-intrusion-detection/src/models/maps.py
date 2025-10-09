import os
import json
import joblib
import uvicorn
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')

class Event(BaseModel):
    # accepts arbitrary features; must match columns.json keys
    features: Dict[str, float]

app = FastAPI(title="ML-IDS Prediction API", version="1.0")

@app.on_event("startup")
def load_artifacts():
    global model, scaler, columns
    model = joblib.load(os.path.join(MODEL_DIR, 'model.joblib'))
    scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.joblib'))
    with open(os.path.join(MODEL_DIR, 'columns.json'), 'r') as f:
        columns = json.load(f)

def build_vector(event_features: Dict[str, Any]) -> np.ndarray:
    # map incoming dict to feature vector order defined by columns.json
    vec = []
    for c in columns:
        # missing feature -> 0.0 (adjust as needed)
        val = event_features.get(c, 0.0)
        vec.append(float(val))
    return np.array(vec).reshape(1, -1)

@app.post("/predict")
def predict(evt: Event):
    try:
        x = build_vector(evt.features)
        x_scaled = scaler.transform(x)
        proba = model.predict_proba(x_scaled)[0]
        pred = int(model.predict(x_scaled)[0])
        # return probability for class '1' (malicious) if binary classes [0,1]
        p_mal = float(proba[1]) if proba.shape[0] > 1 else float(proba[0])
        return {"prediction": pred, "malicious_probability": p_mal}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# run with uvicorn for low latency
if __name__ == "__main__":
    uvicorn.run("predict_server:app", host="0.0.0.0", port=8000, workers=1)