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

# load config
with open(os.path.join(os.path.dirname(__file__), '..', '..', 'configs', 'params.yaml'), 'r') as f:
    params = yaml.safe_load(f)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

# load all processed csvs
files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
if not files:
    raise SystemExit("No processed CSV files found in data/processed/")

df = pd.concat([pd.read_csv(p) for p in files], ignore_index=True)

# Expect a target column 'label'
if 'label' not in df.columns:
    raise SystemExit("Processed data must contain a 'label' column")

# simple preprocessing: drop rows with NaN target
df = df.dropna(subset=['label'])
y = df['label']
X = df.drop(columns=['label'])

# save feature columns
feature_columns = list(X.columns)
with open(os.path.join(MODEL_DIR, 'columns.json'), 'w') as f:
    json.dump(feature_columns, f)

# scale numeric features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X.values)

# train/test split
test_size = params.get('training', {}).get('test_size', 0.2)
rs = params.get('training', {}).get('random_state', 42)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=test_size, random_state=rs, stratify=y)

# instantiate model (RandomForest default)
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

# evaluate
y_pred = model.predict(X_test)
print("Evaluation report:\n", classification_report(y_test, y_pred))

# persist artifacts
joblib.dump(model, os.path.join(MODEL_DIR, 'model.joblib'))
joblib.dump(scaler, os.path.join(MODEL_DIR, 'scaler.joblib'))
print("Saved model, scaler and columns to models/")