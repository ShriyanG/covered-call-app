import os

from config.settings import FEATURES, TICKERS
from src.analysis import Analysis

if __name__ == "__main__":
    # Initialize the Analysis class
    analysis = Analysis()
    # Run Random Forest analysis for each ticker
    for ticker in TICKERS:
        print(f"\nRunning Random Forest analysis for ticker: {ticker}")
        analysis.update_models(ticker, FEATURES)
        print(f"Model and features for {ticker} updated and saved.\n")