import os

from config.settings import OPTIONS_TICKERS
from src.strategy import Strategy

if __name__ == "__main__":
    strategy = Strategy()

    # Loop through all tickers in OPTIONS_TICKERS
    for ticker in OPTIONS_TICKERS:
        print(f"\nProcessing ticker: {ticker}")

        # Loop through both option types: "call" and "put"
        for option_type in ["call", "put"]:
            print(f"\nProcessing {option_type.upper()} option for ticker: {ticker}")

            # Call the predict_option method
            prediction_results = strategy.predict_option(ticker=ticker, option_type=option_type)

            # Print the prediction results
            print("\nPrediction Results:")
            if prediction_results:
                for key, value in prediction_results.items():
                    print(f"{key}: {value}")
            else:
                print("No prediction results available.")