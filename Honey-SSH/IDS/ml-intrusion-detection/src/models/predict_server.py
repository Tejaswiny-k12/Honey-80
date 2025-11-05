import os
import json
import joblib
import uvicorn
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from pathlib import Path
from src.features.extract_features import extract_features_from_text
from Detector import Alert

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / 'models'
CONF = ROOT / 'configs' / 'params.yaml'

class TextEvent(BaseModel):
    text: str
    meta: Dict[str, Any] = {}

app = FastAPI(title="ML-IDS Prediction API")

@app.on_event("startup")
def load_artifacts():
    global model, scaler, columns, threshold
    model = joblib.load(MODEL_DIR / 'model.joblib')
    scaler = joblib.load(MODEL_DIR / 'scaler.joblib')
    with open(MODEL_DIR / 'columns.json', 'r') as f:
        columns = json.load(f)
    # threshold can be set in params.yaml under detection.threshold
    try:
        import yaml
        with open(CONF, 'r') as f:
            cfg = yaml.safe_load(f)
            threshold = float(cfg.get('detection', {}).get('threshold', 0.7))
    except Exception:
        threshold = 0.7

def build_vector_from_features(feat_dict):
    vec = [float(feat_dict.get(c, 0.0)) for c in columns]
    return np.array(vec).reshape(1, -1)

@app.post("/predict_text")
def predict_text(evt: TextEvent):
    try:
        feats = extract_features_from_text(evt.text)
        x = build_vector_from_features(feats)
        x_scaled = scaler.transform(x)
        proba = model.predict_proba(x_scaled)[0]
        pred = int(model.predict(x_scaled)[0])
        # binary: assume class 1 = malicious
        p_mal = float(proba[1]) if proba.shape[0] > 1 else float(proba[0])
        result = {"prediction": pred, "malicious_probability": p_mal, "features": feats}
        if p_mal >= threshold or pred == 1:
            # send alert (non-blocking)
            Alert.send_alert({
                "source": "higpt",
                "text": evt.text,
                "meta": evt.meta,
                "prediction": pred,
                "malicious_probability": p_mal
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("predict_server:app", host="0.0.0.0", port=8000, workers=1)