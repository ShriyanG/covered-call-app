# Configuration settings for the project
# Database configuration

#LOCAL_CONFIG
DB_USER = "shriyangosavi"
DB_PASSWORD = "Risha1234$"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"
DATABASE_URL_LOCAL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

#SUPABASE_CONFIG
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = "Ramkrishnahari124$"  # wrap in quotes if it has special chars like $
SUPABASE_HOST = "db.vxzuilwgslesaqabvumj.supabase.co"
SUPABASE_PORT = 5432
SUPABASE_DB = "postgres"
SUPABASE_DATABASE_URL = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}"

SUPABASE_STORAGE_URL = "https://vxzuilwgslesaqabvumj.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4enVpbHdnc2xlc2FxYWJ2dW1qIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzI1OTgyNSwiZXhwIjoyMDcyODM1ODI1fQ.mB62WVoUSHygK3rT1qIiuSYXHnkH63Pgs0fiivSFgdo"
SUPABASE_BUCKET = 'models'

#POLYGON API SETTINGS
API_KEY = "RLH5skiQVl24hXBE2IyPT3JBDmorI4r0"

#Table names and other settings
DEVIATIONS_TABLE = "stock_deviations"
STOCK_TABLE = "stock_data"
OPTIONS_TABLE = "options_data"
TICKERS = ['AMZN', 'MSFT', 'TSLA', 'GOOG', 'NVDA', 'META', 'AAPL', 'QQQ', 'SPY']
OPTIONS_TICKERS = ['QQQ', 'SPY']
FEATURES = ['rsi_30_diff', 'rsi_70_diff', 'macd', 'price_diff', 'histogram', 'signal', 'rsi', 'bollinger_upper', 'bollinger_lower', 'sma', 'ema_12', 'ema_26']

# NUMERIC SETTINGS
STOP_LOSS = 200  # Stop loss in dollars
BASE_DEVIATION = 5  # Default base deviation in dollars
DEVIATION_BUFFER = 1  # Buffer to add to average deviation
UPPER_THRESHOLD = 0.6  # Threshold to decide 'call' option
LOWER_THRESHOLD = 0.35  # Threshold to decide 'put' option
BEGINNING_DATE = "2023-05-10"  # Date to start fetching stock data from