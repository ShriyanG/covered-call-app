"""
Simple Historical Data Backfill Script

This script backfills historical stock data from Polygon.io into the Supabase database.
Similar to update_stock_data but goes back 5 years from the earliest date in the database.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.src.config.settings import STOCK_TABLE, TICKERS
from app.src.data_inputs import DataInputs


class HistoricalBackfill(DataInputs):
    """Simple historical data backfill using existing DataInputs methods."""

    def get_earliest_date(self, ticker):
        """Get the earliest date for a ticker from the database."""
        engine = self.db_connection.get_engine()
        query = f"SELECT MIN(date) FROM {STOCK_TABLE} WHERE ticker = %s"

        import pandas as pd
        result = pd.read_sql(query, engine, params=(ticker,))
        earliest_date = result.iloc[0, 0]

        if earliest_date is None:
            # If no data exists, use today as the "earliest" date
            return datetime.today().date()

        return earliest_date

    def fetch_historical_data(self, ticker):
        """
        Fetch historical data for a ticker from 2020-01-01 up to earliest date in DB.
        Similar to fetch_recent_data but for historical data.
        """
        # Get earliest date in database
        earliest_date = self.get_earliest_date(ticker)

        # Fetch from 2020-01-01 to day before earliest date in DB
        start_date = '2020-01-01'
        end_date = (earliest_date - timedelta(days=1)).strftime('%Y-%m-%d')

        print(f"Fetching historical data for {ticker} from {start_date} to {end_date}")

        # Use existing stock API to fetch data
        df = self.stock_api.fetch_stock_data(ticker, start_date, end_date)

        if df.empty:
            print(f"No historical data found for {ticker}")
            return df

        # Calculate technical indicators using existing method
        df_with_indicators = self.calculate_technical_indicators(df)
        return df_with_indicators

    def input_historical_stock_data(self, ticker):
        """
        Insert historical stock data into the database.
        Similar to input_stock_data but for historical data.
        """
        # Fetch historical data
        df = self.fetch_historical_data(ticker)

        if df.empty:
            return

        # DEBUG: Print head and tail of dataframe instead of inserting
        print(f"\nDataFrame head for {ticker}:")
        print(df.head())
        print(f"\nDataFrame tail for {ticker}:")
        print(df.tail())
        print(f"Total rows: {len(df)}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")

        # Use existing database insertion logic
        engine = self.db_connection.get_engine()
        query_str = self.db_connection.load_query("insert_or_update_stock_data.sql").format(table_name=STOCK_TABLE)

        from sqlalchemy import text
        query = text(query_str)

        # Execute inserts/updates in a single transaction
        with engine.begin() as connection:
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                # Ensure timestamp compatibility
                if hasattr(row_dict["date"], "to_pydatetime"):
                    row_dict["date"] = row_dict["date"].to_pydatetime()
                connection.execute(query, row_dict)

    def update_historical_stock_data(self):
        """
        Input historical data for all tickers defined in the TICKERS list.
        Similar to update_stock_data but for historical data.
        """
        for ticker in TICKERS:
            print(f"Processing historical data for {ticker}...")
            self.input_historical_stock_data(ticker)
            print(f"Historical data for {ticker} processed successfully.")


def main():
    """Run the historical backfill."""
    backfill = HistoricalBackfill()
    backfill.update_historical_stock_data()


if __name__ == "__main__":
    main()