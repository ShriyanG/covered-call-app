from app.src.data_inputs import DataInputs


def run_update_stock_data():
    data_inputs = DataInputs()
    try:
        data_inputs.update_stock_data()
        data_inputs.update_deviations()
        status = {"success": True, "message": "Stock data and deviations update for all tickers completed successfully!"}
    except Exception as e:
        status = {"success": False, "message": f"An error occurred while updating stock data or deviations: {e}"}
    finally:
        data_inputs.db_connection.close_connection()
    return status

if __name__ == "__main__":
    result = run_update_stock_data()
    print(result["message"])