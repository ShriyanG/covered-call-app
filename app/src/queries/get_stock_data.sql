SELECT *
FROM stock_data
WHERE ticker = %s AND date BETWEEN %s AND %s
ORDER BY date ASC;