import datetime

import pandas as pd
import pandas_market_calendars as mcal

from app.src.config.settings import DEVIATION_BUFFER, OPTIONS_TICKERS
from app.src.data_inputs import DataInputs
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


def calculate_average_deviation_for_period(ticker, start_date, end_date):
    """
    Calculate average daily close-to-close deviation for a ticker over a custom period.
    """
    data_inputs = DataInputs()
    df = data_inputs.get_stock_data(ticker, start_date, end_date)
    if df.empty or "close_price" not in df.columns or len(df) < 2:
        return None

    avg_deviation = df["close_price"].diff().abs().dropna().mean() + DEVIATION_BUFFER
    return {
        "ticker": ticker,
        "start_date": start_date,
        "end_date": end_date,
        "average_deviation": round(avg_deviation, 4),
        "rounded_app_style_deviation": int(round(avg_deviation)),
    }



# Example usage
if __name__ == "__main__":
    deviation_ticker = "QQQ"
    deviation_start_date = "2026-01-01"
    deviation_end_date = datetime.datetime.now().date().strftime("%Y-%m-%d")

    # Test single ticker, single option type
    print("Test predict_options for QQQ, call:")
    print(predict_options("QQQ", "call"))

    print("\nQQQ average deviation for custom period:")
    print(
        calculate_average_deviation_for_period(
            deviation_ticker,
            deviation_start_date,
            deviation_end_date,
        )
    )

    # Test daily options for all tickers
    # print("\nTest predict_daily_options for all tickers:")
    # print(predict_daily_options())