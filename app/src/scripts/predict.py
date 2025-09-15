import datetime

import pandas as pd
import pandas_market_calendars as mcal

from app.src.config.settings import OPTIONS_TICKERS
from app.src.strategy import Strategy


def get_next_nyse_business_day(today=None):
    """
    Returns the next NYSE business day (including today if market is open).
    """
    if today is None:
        today = datetime.datetime.now().date()
    nyse = mcal.get_calendar('NYSE')
    today_ts = pd.Timestamp(today).tz_localize('UTC')
    schedule = nyse.valid_days(start_date=today_ts, end_date=today_ts + pd.Timedelta(days=7))
    if today_ts in schedule:
        return today_ts.date()
    # Otherwise, return the next valid market day
    next_market_days = schedule[schedule > today_ts]
    if len(next_market_days) > 0:
        return next_market_days[0].date()
    return today_ts.date()

def predict_options(ticker, option_type):
    """
    Predict options for a single ticker and option type ('call' or 'put').
    """
    strategy = Strategy()
    result = strategy.predict_option(ticker=ticker, option_type=option_type)
    result["date"] = get_next_nyse_business_day().strftime('%Y-%m-%d')
    return result

def predict_daily_options(option_type="both"):
    """
    Predict daily options for all tickers in OPTIONS_TICKERS.
    If option_type is 'both', returns results for both call and put for each ticker.
    Sets the date field to the next business day.
    """
    results = []
    next_market_day = get_next_nyse_business_day()
    for ticker in OPTIONS_TICKERS:
        for opt in ["call", "put"]:
            prediction = predict_options(ticker, opt)
            if prediction:
                result = {"ticker": ticker, "option_type": opt, **prediction}
                results.append(result)
    return results



# Example usage
if __name__ == "__main__":
    # Test single ticker, single option type
    print("Test predict_options for QQQ, call:")
    print(predict_options("QQQ", "call"))

    # Test daily options for all tickers
    print("\nTest predict_daily_options for all tickers:")
    print(predict_daily_options())