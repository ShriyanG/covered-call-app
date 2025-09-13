import io
import os

import joblib  # For saving and loading models
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from supabase import create_client

from config.settings import SUPABASE_API_KEY, SUPABASE_BUCKET, SUPABASE_STORAGE_URL
from src.data_inputs import DataInputs


class Analysis:
    def __init__(self):
        """
        Initializes the Analysis class and creates a DataInputs object for database interactions.
        """
        self.data_inputs = DataInputs()  # Create an instance of DataInputs

    def split_data(self, df, parameters):
        """
        Splits the data into training and testing sets.

        Parameters:
        - df (pd.DataFrame): The input DataFrame containing features and target.
        - parameters (list): List of feature column names.

        Returns:
        - X_train, X_test, y_train, y_test: Split data for training and testing.
        """
        X = df[parameters]  # Features
        y = df['price_direction']  # Target (up/down movement)

        # Split data into training and testing sets (80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        return X_train, X_test, y_train, y_test

    def train_random_forest(self, X_train, y_train):
        """
        Trains a Random Forest classifier.

        Parameters:
        - X_train (pd.DataFrame): Training features.
        - y_train (pd.Series): Training target.

        Returns:
        - model: Trained Random Forest model.
        """
        # Create a Random Forest classifier with 100 trees
        model = RandomForestClassifier(n_estimators=100, random_state=42)

        # Train the model
        model.fit(X_train, y_train)

        return model

    def analyze_and_prune_features(self, model, X_train, X_test, y_train, y_test, feature_names):
        """
        Computes permutation importance, iteratively prunes features based on importance, 
        and evaluates accuracy for each subset of features.

        Parameters:
        - model: Trained model.
        - X_train (pd.DataFrame): Training features.
        - X_test (pd.DataFrame): Test features.
        - y_train (pd.Series): Training target.
        - y_test (pd.Series): Test target.
        - feature_names (list): List of feature names.

        Returns:
        - pruning_results (list): List of dictionaries with {'num_features', 'features', 'accuracy'}.
        - importance_df (pd.DataFrame): DataFrame of permutation importances.
        """
        # Compute permutation importance
        perm_importance = permutation_importance(
            model, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1
        )

        # Create a DataFrame for permutation importance
        importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance_Mean': perm_importance.importances_mean,
            'Importance_Std': perm_importance.importances_std
        }).sort_values('Importance_Mean', ascending=False)

        # Start pruning features based on importance
        pruning_results = []
        features = list(importance_df['Feature'])  # Start with all features sorted by importance

        while len(features) > 0:
            # Train model with the current feature set
            model.fit(X_train[features], y_train)
            y_pred = model.predict(X_test[features])
            acc = accuracy_score(y_test, y_pred)

            # Store the results
            pruning_results.append({
                'num_features': len(features),
                'features': features.copy(),
                'accuracy': acc
            })

            # Drop the least important feature (last in the list)
            features.pop(-1)

        return pruning_results

    def update_models(self, ticker, parameters):
        """
        Updates models by training, evaluating, and pruning features for the given ticker.

        Parameters:
        - ticker (str): The stock ticker symbol.
        - parameters (list): List of feature column names.
        """
        print(f"Updating models for ticker: {ticker}")

        # Prepare data
        df = self.data_inputs.prepare_classification_data(ticker)
        X_train, X_test, y_train, y_test = self.split_data(df, parameters)

        # Train the model
        model = self.train_random_forest(X_train, y_train)
        results = self.analyze_and_prune_features(model, X_train, X_test, y_train, y_test, parameters)
        
        # Get the best-performing feature set
        best = max(results, key=lambda x: x['accuracy'])
        best_features = best['features']
        print("\nBest Accuracy:", best['accuracy'])
        print("Best Feature Set:", best_features)

        # Train the best model with the best features
        best_model = self.train_random_forest(X_train[best_features], y_train)
        self.data_inputs.db_connection.upload_to_supabase(best_model, ticker, "best_model.pkl")
        self.data_inputs.db_connection.upload_to_supabase(best_features, ticker, "features.pkl")

    def load_best_model(self, ticker):
        """
        Loads the latest best model and features for the given ticker directly from Supabase storage.
        Returns them as in-memory Python objects (not saved to disk).
        """
        supabase = create_client(SUPABASE_STORAGE_URL, SUPABASE_API_KEY)
        bucket = supabase.storage.from_(SUPABASE_BUCKET)

        # Define paths
        model_path = f"{ticker}/best_model.pkl"
        features_path = f"{ticker}/features.pkl"

        # Download as bytes
        model_bytes = bucket.download(model_path)
        features_bytes = bucket.download(features_path)

        # Load directly into memory
        model = joblib.load(io.BytesIO(model_bytes))
        features = joblib.load(io.BytesIO(features_bytes))

        return model, features