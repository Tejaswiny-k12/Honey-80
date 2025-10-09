from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import pandas as pd

def load_data(test_data_path):
    return pd.read_csv(test_data_path)

def load_model(model_path):
    return joblib.load(model_path)

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }

def main(test_data_path, model_path):
    data = load_data(test_data_path)
    X_test = data.drop('label', axis=1)
    y_test = data['label']
    
    model = load_model(model_path)
    
    metrics = evaluate_model(model, X_test, y_test)
    
    print("Evaluation Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python evaluate.py <test_data_path> <model_path>")
    else:
        main(sys.argv[1], sys.argv[2])