INSERT INTO {table_name}
    (ticker, date, open_price, close_price, high_price, low_price, macd, signal, histogram, rsi, bollinger_upper, bollinger_lower)
VALUES 
    (:ticker, :date, :open_price, :close_price, :high_price, :low_price, :macd, :signal, :histogram, :rsi, :bollinger_upper, :bollinger_lower)
ON CONFLICT (ticker, date) 
DO UPDATE SET 
    open_price = EXCLUDED.open_price,
    close_price = EXCLUDED.close_price,
    high_price = EXCLUDED.high_price,
    low_price = EXCLUDED.low_price,
    macd = EXCLUDED.macd,
    signal = EXCLUDED.signal,
    histogram = EXCLUDED.histogram,
    rsi = EXCLUDED.rsi,
    bollinger_upper = EXCLUDED.bollinger_upper,
    bollinger_lower = EXCLUDED.bollinger_lower;