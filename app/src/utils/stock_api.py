import re
import time

import pandas as pd
import requests

from config.settings import API_KEY  # Import the API key from the config file


class StockAPI:
    def __init__(self, api_key):
        """Initialize the Polygon API client."""
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"

    def fetch_stock_data(self, ticker, start_date, end_date):
        """
        Fetches stock data from Polygon API.
        Returns a DataFrame with columns: Date, Open, Close, High, Low.
        """
        # Check if start_date and end_date are the same
        if start_date == end_date:
            return pd.DataFrame()

        url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
        params = {
            "adjusted": True,
            "sort": "asc",
            "limit": 5000,
            "apiKey": self.api_key
        }
        stock_data = []
        while url:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                for result in results:
                    stock_data.append({
                        "ticker": ticker,
                        "date": pd.to_datetime(result["t"], unit='ms').date(),
                        "open_price": result["o"],
                        "close_price": result["c"],
                        "high_price": result["h"],
                        "low_price": result["l"]
                    })
                # Check if there is another page of results
                url = data.get("next_url")
                # Respect API rate limits (5 requests per minute)
                time.sleep(12)
            else:
                print(f"Error fetching data: {response.status_code}, {response.text}")
                break
        return pd.DataFrame(stock_data)

    def generate_option_chain(self, ticker: str, expiration: str, close_price: float, deviation: float, step: float = 1.0) -> dict:
        """
        Generate a dictionary of call and put option symbols within a strike range around a given close price.

        :param ticker: Underlying ticker, e.g., "QQQ"
        :param expiration: Expiration date as "YYYY-MM-DD"
        :param close_price: Current underlying price
        :param deviation: Maximum deviation above/below close price for strike prices
        :param step: Increment for strike prices (default $1)
        :return: Dictionary with keys 'call' and 'put' containing lists of OPRA-style option symbols
        """
        min_strike = close_price - deviation
        max_strike = close_price + deviation

        strikes = []
        current = min_strike
        while current <= max_strike:
            strikes.append(round(current, 2))
            current += step

        option_chain = {"call": [], "put": []}

        for strike in strikes:
            # Format expiration date as YYMMDD
            year = expiration[2:4]
            month = expiration[5:7]
            day = expiration[8:10]
            exp_str = f"{year}{month}{day}"

            # Format strike price: multiply by 1000 and pad to 8 digits
            strike_int = int(round(strike * 1000))
            strike_str = f"{strike_int:08d}"

            # Generate call and put symbols
            option_chain["call"].append(f"O:{ticker}{exp_str}C{strike_str}")
            option_chain["put"].append(f"O:{ticker}{exp_str}P{strike_str}")

        return option_chain

    def get_summary(self, optionsTicker, date, df, ticker, strike_price, option_type, expiration_date):
        """
        Fetch options contract summary for a given ticker and date, and append the data to a DataFrame.

        :param optionsTicker: The options ticker symbol (e.g., "O:QQQ250411P00458000").
        :param date: The date for the options data (YYYY-MM-DD).
        :param df: The DataFrame to which the data will be appended.
        :return: Updated DataFrame with the new data appended.
        """
        # URL for the API
        url = f"{self.base_url}/v1/open-close/{optionsTicker}/{date}"
        # Set up parameters for the API request
        params = {
            'adjusted': 'true',
            "apiKey": self.api_key
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()

            # Extract relevant fields from the response
            row = {
                "date": data.get("from"),
                "symbol": data.get("symbol"),
                "open": data.get("open"),
                "high": data.get("high"),
                "low": data.get("low"),
                "close": data.get("close"),
                "ticker": ticker,  # Use the provided ticker
                "strike_price": strike_price,  # Use the provided strike price
                "option_type": option_type,  # Use the provided option type
                "expiration_date": expiration_date  # Use the provided expiration date
            }
            # Append the row to the DataFrame
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

        return df

    def generate_and_fetch_summary(self, ticker, expiration, close_price, deviation, step=1.0, date=None):
        """
        Generate an option chain, create a DataFrame, and append rows by fetching summaries for each option.

        :param ticker: The underlying stock ticker (e.g., "QQQ").
        :param expiration: The expiration date of the options (YYYY-MM-DD).
        :param close_price: The current close price of the underlying stock.
        :param deviation: The deviation range for strike prices above and below the close price.
        :param step: The increment for strike prices (default is $1).
        :param date: The date for the options data (YYYY-MM-DD). Defaults to today's date if not provided.
        :return: A DataFrame containing the options summary.
        """

        # Generate the option chain
        option_chain = self.generate_option_chain(ticker, expiration, close_price, deviation, step)

        # Create an empty DataFrame with the required columns
        columns = ["date", "symbol", "open", "high", "low", "close",
                "ticker", "strike_price", "option_type", "expiration_date"]
        df = pd.DataFrame(columns=columns)

        # Iterate through the option chain and fetch summaries
        for option_type, symbols in option_chain.items():
            for symbol in symbols:
                # Extract strike price inline using regex
                match = re.search(r"(C|P)(\d{8})$", symbol)
                if not match:
                    raise ValueError(f"Invalid option symbol format: {symbol}")
                strike_price = int(match.group(2)) / 1000

                # Fetch summary and append
                df = self.get_summary(symbol, date, df, ticker, strike_price, option_type, expiration)

        return df