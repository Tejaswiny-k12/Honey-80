from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

def build_features(data):
    """
    Build features from the processed data for the Intrusion Detection System.

    Parameters:
    data (pd.DataFrame): The processed data containing relevant information for feature extraction.

    Returns:
    pd.DataFrame: A DataFrame containing the extracted features.
    """
    # Example feature extraction: Count Vectorization of text data
    vectorizer = CountVectorizer()
    text_features = vectorizer.fit_transform(data['text_column'])  # Replace 'text_column' with the actual column name

    # Convert sparse matrix to DataFrame
    text_features_df = pd.DataFrame(text_features.toarray(), columns=vectorizer.get_feature_names_out())

    # Combine with other features if necessary
    features = pd.concat([data.reset_index(drop=True), text_features_df.reset_index(drop=True)], axis=1)

    return features

def save_features(features, output_path):
    """
    Save the extracted features to a specified output path.

    Parameters:
    features (pd.DataFrame): The DataFrame containing the extracted features.
    output_path (str): The path where the features should be saved.
    """
    features.to_csv(output_path, index=False)  # Save as CSV, adjust format as needed

# Example usage
# if __name__ == "__main__":
#     processed_data = pd.read_csv('data/processed/processed_data.csv')  # Load your processed data
#     features = build_features(processed_data)
#     save_features(features, 'data/processed/features.csv')  # Save the features to a file