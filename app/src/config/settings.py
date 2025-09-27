import os

from dotenv import load_dotenv

load_dotenv()

# Local config
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL_LOCAL = os.getenv("DATABASE_URL_LOCAL")

# Database configuration
SUPABASE_USER = os.getenv("SUPABASE_USER")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
SUPABASE_HOST = os.getenv("SUPABASE_HOST")
SUPABASE_PORT = os.getenv("SUPABASE_PORT")
SUPABASE_DB = os.getenv("SUPABASE_DB")
SUPABASE_DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")

SUPABASE_STORAGE_URL = os.getenv("SUPABASE_STORAGE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SUPABASE_BUCKET = "models"

# Polygon API
API_KEY = os.getenv("API_KEY")

# Table names and other settings
DEVIATIONS_TABLE = os.getenv("DEVIATIONS_TABLE")
STOCK_TABLE = os.getenv("STOCK_TABLE")
OPTIONS_TABLE = os.getenv("OPTIONS_TABLE")

# Lists (comma-separated in .env)
TICKERS = os.getenv("TICKERS", "").split(",")
OPTIONS_TICKERS = os.getenv("OPTIONS_TICKERS", "").split(",")
FEATURES = os.getenv("FEATURES", "").split(",")

# Numeric settings
STOP_LOSS = int(os.getenv("STOP_LOSS", "200"))
BASE_DEVIATION = int(os.getenv("BASE_DEVIATION", "5"))
DEVIATION_BUFFER = int(os.getenv("DEVIATION_BUFFER", "1"))
UPPER_THRESHOLD = float(os.getenv("UPPER_THRESHOLD", "0.6"))
LOWER_THRESHOLD = float(os.getenv("LOWER_THRESHOLD", "0.35"))

# Other settings
BEGINNING_DATE = os.getenv("BEGINNING_DATE", "2020-11-03")
MODEL_TRAINING_START_DATE = os.getenv("MODEL_TRAINING_START_DATE", "2023-05-10")