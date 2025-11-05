import os
import pandas as pd

def load_raw_data(file_path):
    """Load raw data from a specified file path."""
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        raise FileNotFoundError(f"The file {file_path} does not exist.")

def load_interim_data(file_path):
    """Load interim data from a specified file path."""
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        raise FileNotFoundError(f"The file {file_path} does not exist.")

def load_processed_data(file_path):
    """Load processed data from a specified file path."""
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        raise FileNotFoundError(f"The file {file_path} does not exist.")