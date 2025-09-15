INSERT INTO {table_name} (ticker, deviation)
VALUES (:ticker, :deviation)
ON CONFLICT (ticker) DO UPDATE
SET deviation = EXCLUDED.deviation;