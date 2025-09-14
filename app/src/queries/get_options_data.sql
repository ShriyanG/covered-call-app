SELECT *
FROM options_data
WHERE ticker = %s
  AND date = %s
  AND strike_price = %s
  AND option_type = %s
  AND expiration_date = %s;