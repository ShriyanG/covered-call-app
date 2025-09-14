import io
import os

import joblib
import pandas as pd
from sqlalchemy import create_engine
from supabase import create_client

from app.src.config.settings import (
    DATABASE_URL_LOCAL,
    STOCK_TABLE,
    SUPABASE_API_KEY,
    SUPABASE_BUCKET,
    SUPABASE_DATABASE_URL,
    SUPABASE_STORAGE_URL,
)


class DBConnection:
    def __init__(self):
        """Initialize the database connection."""
        try:
            self.engine = create_engine(SUPABASE_DATABASE_URL)
            print("Database connection established successfully.")
        except Exception as e:
            print(f"Error establishing database connection: {e}")
            self.engine = None

    def get_engine(self):
        """Return the SQLAlchemy engine."""
        return self.engine

    def close_connection(self):
        """Close the database connection."""
        if self.engine:
            self.engine.dispose()
            print("Database connection closed successfully.")
        else:
            print("No active database connection to close.")

    def load_query(self, file_name):
        """
        Load an SQL query from the appropriate folder based on the query type.

        :param file_name: Name of the SQL file to load.
        :return: The content of the SQL file as a string.
        """
        queries_dir = os.path.join(os.path.dirname(__file__), "../queries")
        file_path = os.path.join(queries_dir, file_name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Query file '{file_name}' not found in '{queries_dir}' folder.")

        with open(file_path, "r") as file:
            return file.read()

    def upload_to_supabase(self, obj, ticker: str, file_name: str, bucket_name: str = SUPABASE_BUCKET):
        """
        Serialize a Python object with joblib and upload it to Supabase storage.

        Parameters:
        - bucket_name (str): Name of the Supabase storage bucket.
        - remote_path (str): Path inside the bucket where the file should be stored.
        - obj: The Python object (e.g., model, list, dict) to be serialized and uploaded.
        """
        # Create a client
        supabase = create_client(SUPABASE_STORAGE_URL, SUPABASE_API_KEY)
        bucket = supabase.storage.from_(bucket_name)

        remote_path = f"{ticker}/{file_name}"

        # Serialize object to an in-memory buffer
        buffer = io.BytesIO()
        joblib.dump(obj, buffer)
        buffer.seek(0)

        # Upload buffer contents, overwrite if exists
        response = bucket.upload(remote_path, buffer.read(), file_options={"upsert": "true"})
        # Check response status code
        status_code = getattr(response, "status_code", None)
        if status_code == 200 or status_code == 201:
            print(f"Successfully uploaded {file_name} for {ticker} to '{bucket_name}' bucket.")
        else:
            print(f"Failed to upload {file_name} for {ticker} to '{bucket_name}' bucket. Status code: {status_code}")


# Test the connection and query loader
if __name__ == "__main__":
    db_connection = DBConnection()
    engine = db_connection.get_engine()
    ticker = 'QQQ'
    if engine:
        print("Connection test passed!")
        # Test loading a query
        try:
            query = db_connection.load_query("get_most_recent_date.sql").format(table_name=STOCK_TABLE)
            result = pd.read_sql(query, engine, params=(ticker,))
            print("Query loaded successfully:")
            print(result)
        except Exception as e:
            print(f"Error loading query: {e}")
        # Close the engine to release resources
        db_connection.close_connection()
    else:
        print("Connection test failed.")