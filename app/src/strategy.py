import math

import pandas as pd
from sqlalchemy import create_engine

from app.src.analysis import Analysis
from app.src.config.settings import STOCK_TABLE
from app.src.data_inputs import DataInputs  # Import DataInputs


class Strategy:
    def __init__(self):
        """
        Initialize the backtest strategy with a database connection and analysis tools.
        """
        self.data_inputs = DataInputs()
        self.analysis = Analysis()  # Initialize Analysis

    def calc_deviation(self, row, classification_data, model, features, base_deviation,
                       upper_threshold=0.6, lower_threshold=0.35):
        """
        Calculate deviation dynamically based on model prediction and confidence,
        using asymmetric thresholds and rounding to nearest integer for strike prices.

        Parameters:
        - row (pd.Series): A row of stock data.
        - classification_data (pd.DataFrame): DataFrame containing classification data.
        - model: The trained model for making predictions.
        - features (list): List of features used by the model.
        - base_deviation (float): The base deviation value.
        - upper_threshold (float): Threshold for bullish (prob_up).
        - lower_threshold (float): Threshold for bearish (prob_up).

        Returns:
        - int: Rounded deviation to add to the current stock price for the call strike.
        """
        date = row.name  # The index of the row (date)
        if date not in classification_data.index:
            return None

        classification_row = classification_data.loc[date]

        # Restrict to features used by the model
        input_data = pd.DataFrame([classification_row[features].to_dict()])
        prob = model.predict_proba(input_data)[0]
        prob_down, prob_up = prob
        confidence = max(prob)
        if prob_up >= upper_threshold:
            # Bullish → further OTM
            deviation = base_deviation * 1.25 * confidence
        elif prob_up <= lower_threshold:
            # Bearish → closer to ATM
            deviation = base_deviation * prob_up
        else:
            # Neutral → standard deviation
            deviation = base_deviation * confidence
        return deviation

    def calculate_options(self, stock_data, deviation, option_type):
        """
        Calculate options for each row in the stock DataFrame and fetch option data.

        Parameters:
        - stock_data (pd.DataFrame): DataFrame containing stock data.
        - deviation (pd.Series): Series containing deviation values for each row.
        - option_type (str): Option type ('call' or 'put').

        Returns:
        - pd.DataFrame: A new DataFrame containing the fetched option data.
        """
        def fetch_option(row, deviation_value):
            # Example logic for calculating strike price
            if option_type == 'call':
                strike_price = math.ceil(row['close_price'] + deviation_value)
            elif option_type == 'put':
                strike_price = math.floor(row['close_price'] - deviation_value)
            else:
                raise ValueError(f"Invalid option type: {option_type}")

            # Fetch option data using get_option_data
            option_data = self.data_inputs.get_option_data(
                ticker=row['ticker'],
                date=row['date'],
                strike_price=strike_price,
                option_type=option_type,
                expiration_date=row['date']
            )

            # Return the fetched option data or None if no data is found
            return option_data.iloc[0] if not option_data.empty else None

        # Create a new DataFrame to store option data
        option_columns = ['strike_price', 'open', 'high', 'low', 'close']
        options_df = pd.DataFrame(columns=option_columns, index=stock_data.index)

        # Populate the options DataFrame
        for idx, row in stock_data.iterrows():
            deviation_value = deviation[idx]
            option_data = fetch_option(row, deviation_value)
            if option_data is not None:
                # Add the valid option data to the DataFrame
                options_df.loc[idx] = [
                    option_data['strike_price'],
                    option_data['open'],
                    option_data['high'],
                    option_data['low'],
                    option_data['close'],
                ]

        return options_df

    def load_data(self, ticker, start_date, end_date, base_deviation=0, option_type='call'):
        """
        Load stock data for the given ticker and date range, and calculate options.

        Parameters:
        - ticker (str): Stock ticker symbol.
        - start_date (str): Start date in 'YYYY-MM-DD' format.
        - end_date (str): End date in 'YYYY-MM-DD' format.
        - base_deviation (float): Base deviation value for calculating the option strike price.
        - option_type (str): Option type ('call' or 'put').

        Returns:
        - pd.DataFrame: A DataFrame containing the fetched option data.
        """
        print(f"Loading stock data for ticker: {ticker}, from {start_date} to {end_date}")
        stock_data = self.data_inputs.get_stock_data(ticker, start_date, end_date)

        # Load the best model for the ticker
        model, features = self.analysis.load_best_model(ticker)
        classification_data = self.data_inputs.prepare_classification_data(ticker, backtest=True)

        # Set the index of stock_data to 'date'
        if 'date' in stock_data.columns:
            stock_data.set_index('date', inplace=True, drop=False)

        # Set the index of classification_data to 'date'
        if 'date' in classification_data.columns:
            classification_data.set_index('date', inplace=True, drop=False)

        # Calculate deviation dynamically for each row
        stock_data['deviation'] = stock_data.apply(
            lambda row: self.calc_deviation(row, classification_data, model, features, base_deviation), axis=1
        )
        # Drop rows where deviation could not be calculated (NaN values)
        stock_data = stock_data.dropna(subset=['deviation'])

        # Calculate options and return the options DataFrame
        options_data = self.calculate_options(stock_data, deviation=stock_data['deviation'], option_type=option_type)
        return options_data

    def backtest(self, ticker, start_date, end_date, base_deviation=0, option_type='call', stop_loss=50):
        """
        Run the backtest strategy for selling same-day call options.

        Parameters:
        - ticker (str): Stock ticker symbol.
        - start_date (str): Start date in 'YYYY-MM-DD' format.
        - end_date (str): End date in 'YYYY-MM-DD' format.
        - base_deviation (float): Base deviation value for calculating the option strike price.
        - option_type (str): Option type ('call' or 'put').
        - stop_loss (float): Stop loss threshold in cents (e.g., 50 = $0.50).

        Returns:
        - dict: Summary of the backtest results.
        """
        options_data = self.load_data(ticker, start_date, end_date, base_deviation, option_type)
        if options_data is None or options_data.empty:
            print("No options data available for backtesting.")
            return {}

        profit = 0
        total_trades = 0
        successful_trades = 0
        stop_losses_hit = 0
        successful_trade_profit = 0
        negative_trades = 0
        neutral_trades = 0

        for idx, row in options_data.iterrows():
            opening_price = row['open'] * 100
            closing_price = row['close'] * 100
            high_price = row['high'] * 100

            # Check if any option price is NaN
            if pd.isna(opening_price) or pd.isna(closing_price) or pd.isna(high_price):
                continue

            # Check for stop loss
            if high_price >= opening_price + stop_loss: 
                loss = (opening_price - (opening_price + stop_loss)) 
                profit += loss
                total_trades += 1
                stop_losses_hit += 1
                continue

            # Calculate profit or loss if stop loss is not triggered
            trade_profit = (opening_price - closing_price)
            profit += trade_profit
            total_trades += 1

            if closing_price < opening_price:
                # Successful trade
                successful_trades += 1
                successful_trade_profit += trade_profit
            elif closing_price > opening_price:
                # Negative trade (loss without stop loss being hit)
                negative_trades += 1
            else: 
                neutral_trades += 1

        # Calculate average gain per successful trade
        avg_gain_per_successful_trade = (
            successful_trade_profit / successful_trades
            if successful_trades > 0
            else 0
        )

        return {
            'total_profit': profit,     
            'total_trades': total_trades,
            'successful_trades': successful_trades,
            'stop_losses_hit': stop_losses_hit,
            'negative_trades': negative_trades,
            'neutral_trades': neutral_trades,
            'success_rate': (successful_trades / total_trades * 100) if total_trades > 0 else 0,
            'avg_gain_per_successful_trade': avg_gain_per_successful_trade,
        }

    def predict_option(self, ticker, option_type, deviation=5, upper_threshold=0.6, lower_threshold=0.35):
        """
        Predict the option to purchase based on the most recent data.

        Parameters:
        - ticker (str): The stock ticker symbol (e.g., "QQQ").
        - option_type (str): The type of option ("call" or "put").

        Returns:
        - dict: A dictionary containing the prediction, probabilities, and option strike price.
        """
        limit = 1
        # Fetch the most recent business day data
        query = self.data_inputs.db_connection.load_query("fetch_recent_data.sql").format(table_name=STOCK_TABLE)
        last_day = pd.read_sql(query, self.data_inputs.db_connection.engine, params=(ticker, limit))
        recent_data = self.data_inputs.prepare_classification_data(ticker=ticker, backtest=True)
        model, features = self.analysis.load_best_model(ticker)
        if recent_data.empty:
            print("No recent data found for the ticker.")
            return None
        last_row = recent_data.tail(1)
        input_data = last_row[features]

        # Run the model's predict method using the filtered values
        prediction = model.predict(input_data)
        prediction_proba = model.predict_proba(input_data)

        # Calculate the deviation to determine the exact option to purchase
        base_deviation = deviation
        upper_threshold = upper_threshold
        lower_threshold = lower_threshold

        # Call calc_deviation
        deviation = self.calc_deviation(
            row=last_row.iloc[0],  
            classification_data=recent_data,
            model=model,
            features=features,
            base_deviation=base_deviation,
            upper_threshold=upper_threshold,
            lower_threshold=lower_threshold
        )

        # Determine the option strike price
        close_price = last_day['close_price'].values[0]
        print("close price: ", close_price, " deviation: ", deviation, "base deviation: ", base_deviation)
        if option_type == 'call':
            option_strike_price = math.ceil(close_price + deviation)
        elif option_type == 'put':
            option_strike_price = math.floor(close_price - deviation)
        else:
            raise ValueError(f"Invalid option type: {option_type}")

        print(f"Option strike price to purchase for {option_type.upper()} option: {option_strike_price}")

        result = {
            "ticker": ticker,
            "option_type": option_type.upper(),
            "prediction": prediction[0],
            "probabilities": prediction_proba[0],
            "deviation": deviation,
            "option_strike_price": option_strike_price,
        }
        return self.data_inputs.db_connection.clean_prediction_result(result)


if __name__ == "__main__":
    strategy = Strategy()
    ticker = "QQQ"
    start_date = "2025-01-01"
    end_date = "2025-09-12"
    base_deviation = 5
    option_type = "call"
    stop_loss = 200
    backtest_results = strategy.backtest(ticker=ticker, start_date=start_date, end_date=end_date, base_deviation=base_deviation, option_type=option_type, stop_loss=stop_loss)

    # Print the backtest results
    print("\nBacktest Results:")
    for key, value in backtest_results.items():
        print(f"{key}: {value}")