SELECT
    date,
    close_price,
    rsi,
    macd,
    signal,
    histogram,
    bollinger_upper,
    bollinger_lower
FROM {table_name}
WHERE ticker = %s AND date >= %s
ORDER BY date ASC;