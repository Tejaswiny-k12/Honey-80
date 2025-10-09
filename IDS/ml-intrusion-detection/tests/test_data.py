import pytest
from src.data.loader import load_data
from src.data.preprocess import preprocess_data

def test_load_data():
    # Test loading of raw data
    data = load_data('data/raw/sample_data.csv')
    assert data is not None
    assert len(data) > 0

def test_preprocess_data():
    # Test preprocessing of data
    raw_data = load_data('data/raw/sample_data.csv')
    processed_data = preprocess_data(raw_data)
    assert processed_data is not None
    assert 'feature_column' in processed_data.columns
    assert processed_data.shape[0] > 0  # Ensure some rows are returned after preprocessing