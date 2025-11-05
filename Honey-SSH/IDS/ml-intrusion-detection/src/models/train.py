import os
import glob
import json
import joblib
import yaml
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from pathlib import Path
from src.features.extract_features import extract_features_from_text

ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / 'configs' / 'params.yaml', 'r') as f:
    params = yaml.safe_load(f)

# data dirs (merge two projects)
data_dirs = [
    ROOT / 'data' / 'processed',
    Path(r'C:\Users\teju\Desktop\Honey-SSH\IDS\Intrusion-Detection-System-Using-Machine-Learning') / 'data' / 'processed'
]
rows = []
for d in data_dirs:
    for p in glob.glob(str(d / '*.csv')):
        df = pd.read_csv(p)
        rows.append(df)
if not rows:
    raise SystemExit("No processed CSV files found in any processed data directories.")
df = pd.concat(rows, ignore_index=True)

if 'label' not in df.columns:
    raise SystemExit("Processed CSVs must include a 'label' column (0 benign / 1 malicious).")

# If payload/text present, compute text features and append as columns
text_cols = []
if 'payload' in df.columns or 'message' in df.columns:
    tcol = 'payload' if 'payload' in df.columns else 'message'
    txt_feats = df[tcol].fillna('').astype(str).apply(lambda s: extract_features_from_text(s))
    txt_df = pd.DataFrame(list(txt_feats))
    df = pd.concat([df.reset_index(drop=True), txt_df.reset_index(drop=True)], axis=1)
    text_cols = list(txt_df.columns)

# drop non-feature columns (keep numeric features and encoded features)
non_feature_cols = [c for c in ['payload', 'message', 'timestamp', 'id'] if c in df.columns]
X = df.drop(columns=non_feature_cols + ['label']).fillna(0)
y = df['label'].astype(int)

# ensure numeric
X = X.apply(pd.to_numeric, errors='coerce').fillna(0)

# save feature columns
MODEL_DIR = ROOT / 'models'
MODEL_DIR.mkdir(parents=True, exist_ok=True)
feature_columns = list(X.columns)
with open(MODEL_DIR / 'columns.json', 'w') as f:
    json.dump(feature_columns, f)

# scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X.values)

# split
test_size = params.get('training', {}).get('test_size', 0.2)
rs = params.get('training', {}).get('random_state', 42)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=test_size, random_state=rs, stratify=y)

rf_params = {
    'n_estimators': params.get('n_estimators', 100),
    'max_depth': params.get('max_depth', None),
    'min_samples_split': params.get('min_samples_split', 2),
    'min_samples_leaf': params.get('min_samples_leaf', 1),
    'random_state': params.get('random_state', 42),
    'n_jobs': -1
}
model = RandomForestClassifier(**rf_params)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("Evaluation report:\n", classification_report(y_test, y_pred))

joblib.dump(model, MODEL_DIR / 'model.joblib')
joblib.dump(scaler, MODEL_DIR / 'scaler.joblib')
print(f"Saved model artifacts to {MODEL_DIR}")