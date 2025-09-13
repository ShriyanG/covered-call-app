from src.data_inputs import DataInputs

if __name__ == "__main__":
    # Initialize the DataInputs class
    data_inputs = DataInputs()

    print("Updating options data for all tickers...")
    try:
        # Call the update_options_data function to update all tickers
        data_inputs.update_options_data()
        print("Options data update for all tickers completed successfully!")
    except Exception as e:
        print(f"An error occurred while updating options data: {e}")
    finally:
        # Close the database connection
        data_inputs.db_connection.close_connection()