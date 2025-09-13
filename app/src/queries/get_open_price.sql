SELECT open_price
FROM {table_name}
WHERE ticker = %s AND date = %s;