from sklearn.externals import joblib
import pandas as pd

def load_model(model_path):
    """Load the trained model from the specified path."""
    model = joblib.load(model_path)
    return model

def make_prediction(model, data):
    """Make predictions using the trained model."""
    predictions = model.predict(data)
    return predictions

def predict(model_path, input_data):
    """Load the model and make predictions on the input data."""
    model = load_model(model_path)
    predictions = make_prediction(model, input_data)
    return predictions

if __name__ == "__main__":
    # Example usage
    model_path = 'path/to/your/model.pkl'  # Update with your model path
    input_data = pd.read_csv('path/to/your/input_data.csv')  # Update with your input data path
    predictions = predict(model_path, input_data)
    print(predictions)