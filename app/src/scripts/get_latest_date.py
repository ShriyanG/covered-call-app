import datetime

import pandas as pd
import pandas_market_calendars as mcal

from app.src.config.settings import STOCK_TABLE
from app.src.utils.db_connection import DBConnection


def get_latest_dates():
    db_connection = DBConnection()
    engine = db_connection.get_engine()
    latest_date = None
    if engine:
        try:
            query = db_connection.load_query("get_max_date.sql").format(table_name=STOCK_TABLE)
            result = pd.read_sql(query, engine)
            if not result.empty:
                latest_date = str(result.iloc[0, 0])
        except Exception as e:
            print(f"Error loading query: {e}")
        db_connection.close_connection()
        
    # Get latest stock market day
    nyse = mcal.get_calendar('NYSE')
    today = datetime.datetime.now()
    schedule = nyse.valid_days(start_date='2025-01-01', end_date=today)
    last_market_day = schedule[-1].strftime('%Y-%m-%d')
    return latest_date, last_market_day