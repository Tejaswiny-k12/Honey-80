import os
from src.data.loader import load_data
from src.data.preprocess import preprocess_data
from src.features.build_features import create_features
from src.models.train import train_model
from src.evaluation.evaluate import evaluate_model

def main():
    # Load raw data
    raw_data = load_data(os.path.join('data', 'raw'))
    
    # Preprocess the data
    processed_data = preprocess_data(raw_data)
    
    # Create features for modeling
    features = create_features(processed_data)
    
    # Train the model
    model = train_model(features)
    
    # Evaluate the model
    evaluation_results = evaluate_model(model, features)
    
    print("Evaluation Results:", evaluation_results)

if __name__ == "__main__":
    main()