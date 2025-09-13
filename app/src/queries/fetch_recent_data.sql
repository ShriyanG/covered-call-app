SELECT *
FROM {table_name}
WHERE ticker = %s
ORDER BY date DESC
LIMIT %s;