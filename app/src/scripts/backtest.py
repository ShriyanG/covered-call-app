import matplotlib.pyplot as plt

from app.src.strategy import Strategy


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

if __name__ == "__main__":
    # Example usage for manual testing
    ticker = "QQQ"
    start_date = "2025-01-01"
    end_date = "2025-09-12"
    base_deviation = 5
    option_type = "call"
    stop_loss = 200
    backtest_results = run_backtest(ticker, start_date, end_date, base_deviation, option_type, stop_loss)
    print("\nBacktest Results:")
    for key, value in backtest_results.items():
        print(f"{key}: {value}")