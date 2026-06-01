from app.src.strategy import Strategy
from app.src.data_inputs import DataInputs


def run_backtest(ticker, start_date, end_date, base_deviation, option_type, stop_loss):
    """
    Run the backtest strategy and return results.
    """
    strategy = Strategy()
    results = strategy.backtest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        base_deviation=base_deviation,
        option_type=option_type,
        stop_loss=stop_loss
    )
    return results


def calculate_average_deviation_for_period(ticker, start_date, end_date):
    """
    Calculate the average absolute daily close-to-close deviation for a ticker
    between the provided start and end dates.
    """
    data_inputs = DataInputs()
    stock_data = data_inputs.get_stock_data(ticker, start_date, end_date)
    if stock_data.empty or "close_price" not in stock_data.columns or len(stock_data) < 2:
        return None

    avg_close_deviation = float(stock_data["close_price"].diff().abs().dropna().mean())
    
    average_daily_deviation = None
    if "high" in stock_data.columns and "low" in stock_data.columns:
        average_daily_deviation = float((stock_data["high"] - stock_data["low"]).abs().dropna().mean())
    elif "high_price" in stock_data.columns and "low_price" in stock_data.columns:
        average_daily_deviation = float((stock_data["high_price"] - stock_data["low_price"]).abs().dropna().mean())

    result = {
        "ticker": ticker,
        "start_date": start_date,
        "end_date": end_date,
        "average_close_deviation": round(avg_close_deviation, 4),
        "average_daily_deviation": round(average_daily_deviation, 4) if average_daily_deviation is not None else None,
        "rounded_deviation": int(round(avg_close_deviation)),
    }
    return result


if __name__ == "__main__":
    # Example usage for manual testing
    ticker = "QQQ"
    start_date = "2026-01-01"
    end_date = "2026-05-30"
    base_deviation = 6
    option_type = "call"
    stop_loss = 25
    backtest_results = run_backtest(ticker, start_date, end_date, base_deviation, option_type, stop_loss)
    print("\nBacktest Results:")
    for key, value in backtest_results.items():
        if key != "profit_curve":
            print(f"{key}: {value}")

    # avg_dev_result = calculate_average_deviation_for_period(ticker, start_date, end_date)
    # print("\nQQQ average daily deviation from start_date to end_date:")
    # print(avg_dev_result)