INSERT INTO {table_name} (date, symbol, ticker, option_type, open, high, low, close, strike_price, expiration_date)
VALUES (:date, :symbol, :ticker, :option_type, :open, :high, :low, :close, :strike_price, :expiration_date)
ON CONFLICT (date, symbol, option_type) DO NOTHING;