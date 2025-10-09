from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

def load_data(file_path):
    """Load raw data from a specified file path."""
    data = pd.read_csv(file_path)
    return data

def clean_data(data):
    """Clean the dataset by handling missing values and duplicates."""
    data = data.drop_duplicates()
    data = data.fillna(method='ffill')  # Forward fill for missing values
    return data

def transform_data(data):
    """Transform the dataset by scaling numerical features."""
    scaler = StandardScaler()
    numerical_features = data.select_dtypes(include=[np.number]).columns.tolist()
    data[numerical_features] = scaler.fit_transform(data[numerical_features])
    return data

def preprocess(file_path):
    """Main preprocessing function to load, clean, and transform data."""
    raw_data = load_data(file_path)
    cleaned_data = clean_data(raw_data)
    processed_data = transform_data(cleaned_data)
    return processed_data