import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sqlalchemy import text  # Import `text` from SQLAlchemy

from app.src.config.settings import (
    API_KEY,
    BEGINNING_DATE,
    DEVIATION_BUFFER,
    DEVIATIONS_TABLE,
    OPTIONS_TABLE,
    OPTIONS_TICKERS,
    STOCK_TABLE,
    TICKERS,
)
from app.src.utils.db_connection import DBConnection
from app.src.utils.stock_api import StockAPI


class DataInputs:
    def __init__(self):
        """
        Initialize the DataInputs class by instantiating the database connection
        and stock API client.
        """
        self.db_connection = DBConnection()
        self.stock_api = StockAPI(api_key=API_KEY)  # Replace with your actual API key

    def calculate_technical_indicators(self, df):
        df['macd'] = df['close_price'].ewm(span=12, adjust=False).mean() - df['close_price'].ewm(span=26, adjust=False).mean()
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['histogram'] = df['macd'] - df['signal']
        delta = df['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        df['SMA_20'] = df['close_price'].rolling(window=20).mean()
        df['bollinger_upper'] = df['SMA_20'] + 2 * df['close_price'].rolling(window=20).std()
        df['bollinger_lower'] = df['SMA_20'] - 2 * df['close_price'].rolling(window=20).std()
        df = df.drop(columns=['SMA_20'])
        df = df.iloc[26:].reset_index(drop=True)
        return df

    def get_most_recent_date(self, table_name, ticker):
        """
        Fetch the most recent date for a given ticker from the database and return the next day's date.
        """
        engine = self.db_connection.get_engine()
        query = self.db_connection.load_query("get_most_recent_date.sql").format(table_name=table_name)
        
        result = pd.read_sql(query, engine, params=(ticker,))
        most_recent_date = result.iloc[0, 0]
        most_recent_date = pd.to_datetime(most_recent_date)
        next_day = most_recent_date + timedelta(days=1)
        return next_day.strftime('%Y-%m-%d')

    def fetch_recent_data(self, table_name, ticker, limit=30):
        """
        Fetch the most recent `limit` rows for a ticker from the SQL table.
        """
        engine = self.db_connection.get_engine()
        query = self.db_connection.load_query("fetch_recent_data.sql").format(table_name=table_name)
        
        # Fetch the most recent rows from the database
        df = pd.read_sql(query, engine, params=(ticker, limit))
        df = df.sort_values("date", ascending=True).reset_index(drop=True)
        
        # Fetch additional data from the stock API
        start_date = self.get_most_recent_date(table_name, ticker)
        end_date = datetime.today().strftime('%Y-%m-%d')
        df_append = self.stock_api.fetch_stock_data(ticker, start_date, end_date)
        
        # Combine and calculate indicators
        df_combined = pd.concat([df, df_append], ignore_index=True)
        df_with_indicators = self.calculate_technical_indicators(df_combined)
        return df_with_indicators

    def input_stock_data(self, ticker):
        """
        Insert or update stock data into the database using a query from db_queries.

        :param ticker: Stock ticker symbol.
        """
        # Fetch recent stock data
        df = self.fetch_recent_data(table_name=STOCK_TABLE, ticker=ticker, limit=30)
        engine = self.db_connection.get_engine()

        # Load SQL query string and substitute table name before text()
        query_str = self.db_connection.load_query(
            "insert_or_update_stock_data.sql"
        ).format(table_name=STOCK_TABLE)
        query = text(query_str)

        # Execute inserts/updates in a single transaction
        with engine.begin() as connection:
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                # Ensure timestamp compatibility
                if hasattr(row_dict["date"], "to_pydatetime"):
                    row_dict["date"] = row_dict["date"].to_pydatetime()
                connection.execute(query, row_dict)

    def update_stock_data(self):
        """
        Input data for all tickers defined in the TICKERS list.
        """
        for ticker in TICKERS:
            print(f"Processing data for {ticker}...")
            self.input_stock_data(ticker)
            print(f"Data for {ticker} processed successfully.")

    def get_open_price(self, ticker, date):
        """
        Fetch the open_price for a given ticker and date from the STOCK_TABLE, rounded to the nearest integer.

        :param ticker: The stock ticker symbol (e.g., "QQQ").
        :param date: The date for which to fetch the open_price (YYYY-MM-DD).
        :return: The open_price (rounded to the nearest integer) for the given ticker and date, or None if not found.
        """
        try:
            engine = self.db_connection.get_engine()
            query = self.db_connection.load_query("get_open_price.sql").format(table_name=STOCK_TABLE)
            result = pd.read_sql(query, engine, params=(ticker, date))  # Pass parameters as a tuple
            if not result.empty:
                open_price = result.iloc[0, 0]  # Fetch the open_price
                return round(open_price)  # Round to the nearest integer
            else:
                return None
        except Exception as e:
            print(f"Error fetching open_price for ticker '{ticker}' on date '{date}': {e}")
            return None
        
    def get_options_date_range(self, ticker):
        """
        Fetch the most recent date from the OPTIONS_TABLE and create a dictionary of dates
        to iterate through from the most recent options date to the most recent stock date (exclusive),
        with the open_price as the value for each date.

        :param ticker: The stock ticker symbol (e.g., "QQQ").
        :return: A dictionary with dates as keys and open_price as values.
        """
        try:
            # Fetch the most recent date from the OPTIONS_TABLE
            options_date = self.get_most_recent_date(OPTIONS_TABLE, ticker)
            options_date = pd.to_datetime(options_date)

            # Fetch the most recent date from the STOCK_TABLE
            stock_date = self.get_most_recent_date(STOCK_TABLE, ticker)
            stock_date = pd.to_datetime(stock_date)

            # Calculate the date range (up to but not including the stock_date)
            start_date = options_date  # Start from the most recent options date
            end_date = stock_date - timedelta(days=1)  # Exclude the stock_date
            date_range = pd.date_range(start=start_date, end=end_date).tolist()

            # Create a dictionary with dates as keys and open_price as values
            date_open_price_dict = {}
            for date in date_range:
                open_price = self.get_open_price(ticker, date.date())  # Fetch open_price for the date
                if open_price is not None:  # Only add dates with valid open_price
                    date_open_price_dict[date.date()] = open_price

            return date_open_price_dict
        except Exception as e:
            print(f"Error fetching date range for ticker '{ticker}': {e}")
            return {}

    def input_options_data(self, ticker):
        """
        Fetch the options date range, generate and fetch summaries for each date, 
        and insert the data into the OPTIONS_TABLE.

        :param ticker: The stock ticker symbol (e.g., "QQQ").
        """
        try:
            # Fetch the options date range with open prices
            date_open_price_dict = self.get_options_date_range(ticker)

            if not date_open_price_dict:
                print(f"No valid date range or open prices found for ticker '{ticker}'.")
                return

            # Initialize the database engine
            engine = self.db_connection.get_engine()

            # Load the SQL query for inserting options data
            query_str = self.db_connection.load_query("insert_options_data.sql").format(table_name=OPTIONS_TABLE)
            query = text(query_str)

            # Iterate through the date and open price dictionary
            for date, open_price in date_open_price_dict.items():

                # Generate and fetch the options summary for the date
                options_summary_df = self.stock_api.generate_and_fetch_summary(
                    ticker=ticker,
                    expiration=date.strftime('%Y-%m-%d'),
                    close_price=open_price,
                    deviation=6,  # Example deviation value
                    step=1.0,
                    date=date.strftime('%Y-%m-%d')
                )

                if options_summary_df.empty:
                    print(f"No options data found for ticker '{ticker}' on date '{date}'. Skipping...")
                    continue

                # Insert the options data into the OPTIONS_TABLE
                with engine.begin() as connection:
                    for _, row in options_summary_df.iterrows():
                        row_dict = row.to_dict()
                        # Ensure timestamp compatibility
                        if hasattr(row_dict["date"], "to_pydatetime"):
                            row_dict["date"] = row_dict["date"].to_pydatetime()
                        connection.execute(query, row_dict)

        except Exception as e:
            print(f"Error processing options data for ticker '{ticker}': {e}")
    
    def update_options_data(self):
        """
        Input options data for all tickers defined in the TICKERS list.
        """
        for ticker in OPTIONS_TICKERS:
            print(f"Processing options data for {ticker}...")
            self.input_options_data(ticker)
            print(f"Options data for {ticker} processed successfully.")

    def prepare_classification_data(self, ticker, table_name='stock_data', sma_period=20, backtest=False):
        """
        Prepares the classification data for a given ticker from the stock data table.

        The function calculates the absolute difference of RSI from 30 and 70, 
        the MACD, the price difference, and the next day's price movement (up/down).

        Parameters:
        - ticker (str): The stock ticker symbol.
        - table_name (str): The name of the table containing the stock data in SQL (default: 'stock_data').
        - sma_period (int): The period for calculating the simple moving average (default: 20).
        - backtest (bool): If True, include the 'date' column in the returned DataFrame.

        Returns:
        - pd.DataFrame: DataFrame with features and target for classification.
        """
        try:
            # Set up database connection
            engine = self.db_connection.get_engine()

            # Load the SQL query for fetching stock data
            query = self.db_connection.load_query("get_stock_data_for_classification.sql").format(table_name=table_name)

            # Execute the query and fetch the data
            df = pd.read_sql(query, engine, params=(ticker,))  # Pass parameters as a tuple

            # Calculate next day price change
            df['next_day_close'] = df['close_price'].shift(-1)
            df['next_day_change'] = df['next_day_close'] - df['close_price']

            # Calculate SMA, EMA, and other features
            df['sma'] = df['close_price'].rolling(window=sma_period).mean()
            df['ema_12'] = df['close_price'].ewm(span=12, adjust=False).mean()
            df['ema_26'] = df['close_price'].ewm(span=26, adjust=False).mean()

            # Discretize the price movement: 1 for up, 0 for down or no change
            df['price_direction'] = (df['next_day_change'] > 0).astype(int)

            # Calculate RSI-based features
            df['rsi_30_diff'] = abs(df['rsi'] - 30)  # Absolute difference from 30
            df['rsi_70_diff'] = abs(df['rsi'] - 70)  # Absolute difference from 70

            # Calculate price difference from previous day's close
            df['prev_close'] = df['close_price'].shift(1)  # Previous day's close
            df['price_diff'] = df['close_price'] - df['prev_close']  # Difference in closing prices

            # Select columns to return
            columns_to_return = [
                'rsi_30_diff', 'rsi_70_diff', 'macd', 'price_diff', 'price_direction',
                'histogram', 'signal', 'rsi', 'bollinger_upper', 'bollinger_lower',
                'sma', 'ema_12', 'ema_26'
            ]
            
            # If backtest is True, include the 'date' column
            if backtest:
                columns_to_return.insert(0, 'date')

            # Drop rows with NaNs only in the specified columns
            df = df.dropna(subset=columns_to_return).reset_index(drop=True)

            return df[columns_to_return]
        except Exception as e:
            print(f"Error preparing classification data for ticker '{ticker}': {e}")
            return pd.DataFrame()

    def get_stock_data(self, ticker, start_date, end_date):
        """
        Fetch stock data for the given ticker and date range.

        Parameters:
        - ticker (str): Stock ticker symbol.
        - start_date (str): Start date in 'YYYY-MM-DD' format.
        - end_date (str): End date in 'YYYY-MM-DD' format.

        Returns:
        - pd.DataFrame: Stock data.
        """
        try:
            engine = self.db_connection.get_engine()
            query = self.db_connection.load_query("get_stock_data.sql")
            df = pd.read_sql(query, engine, params=(ticker, start_date, end_date))
            return df
        except Exception as e:
            print(f"Error fetching stock data for ticker '{ticker}' between '{start_date}' and '{end_date}': {e}")
            return pd.DataFrame()

    def get_option_data(self, ticker, date, strike_price, option_type, expiration_date):
        """
        Fetch option data for the given parameters.

        Parameters:
        - ticker (str): Stock ticker symbol.
        - date (str): Date in 'YYYY-MM-DD' format.
        - strike_price (float): Strike price of the option.
        - option_type (str): Option type ('call' or 'put').

        Returns:
        - pd.DataFrame: Option data.
        """
        try:
            # Set up database connection
            engine = self.db_connection.get_engine()
            query = self.db_connection.load_query("get_options_data.sql")
            df = pd.read_sql(query, engine, params=(ticker, date, strike_price, option_type, expiration_date))
            return df
        except Exception as e:
            print(f"Error fetching option data for ticker '{ticker}' on '{date}' with strike price '{strike_price}' and option type '{option_type}': {e}")
            return pd.DataFrame()

    def calculate_average_deviation(self, ticker):
        """
        Fetches closing prices for ticker for previous x days, calculates average deviation.
        ticker: str
        days: int
        Returns: int (rounded average deviation)
        """
        today = datetime.today().strftime('%Y-%m-%d')
        df = self.get_stock_data(ticker, BEGINNING_DATE, today)
        if df.empty or 'close_price' not in df.columns:
            return None
        prices = df['close_price'].tolist()
        diffs = np.diff(prices)
        deviations = np.abs(diffs)
        avg_deviation = np.mean(deviations) + DEVIATION_BUFFER
        return int(round(avg_deviation))

    def update_deviations(self):
        """
        For each ticker, calculate average deviation and upsert into deviations table using upsert_deviation.sql.
        """
        engine = self.db_connection.get_engine()
        update_query_str = self.db_connection.load_query("update_deviation.sql").format(table_name=DEVIATIONS_TABLE)
        update_query = text(update_query_str)

        # Execute upserts in a single transaction
        with engine.begin() as connection:
            for ticker in TICKERS:
                avg_dev = self.calculate_average_deviation(ticker)
                if avg_dev is not None:
                    connection.execute(update_query, {"ticker": ticker, "deviation": avg_dev})

    def get_stock_deviation(self, ticker):
        """
        Fetch the numeric deviation for a given ticker from the deviations table.
        Returns the deviation as an integer, or None if not found.
        """
        try:
            engine = self.db_connection.get_engine()
            query = self.db_connection.load_query("get_stock_deviation.sql").format(table_name=DEVIATIONS_TABLE)
            result = pd.read_sql(query, engine, params=(ticker,))
            if not result.empty:
                deviation = result.iloc[0, 0]
                return int(deviation)
            else:
                return None
        except Exception as e:
            print(f"Error fetching deviation for ticker '{ticker}': {e}")
            return None