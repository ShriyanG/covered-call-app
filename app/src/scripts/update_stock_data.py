from src.data_inputs import DataInputs

if __name__ == "__main__":
    # Initialize the DataInputs class
    data_inputs = DataInputs()

    print("Updating data for all tickers...")
    try:
        # Call the update_stock_data function to update all tickers
        data_inputs.update_stock_data()
        print("Data update for all tickers completed successfully!")
    except Exception as e:
        print(f"An error occurred while updating data: {e}")
    finally:
        # Close the database connection
        data_inputs.db_connection.close_connection()