from app.src.data_inputs import DataInputs


def run_update_options_data():
    data_inputs = DataInputs()
    try:
        data_inputs.update_options_data()
        status = {"success": True, "message": "Options data update for all tickers completed successfully!"}
    except Exception as e:
        status = {"success": False, "message": f"An error occurred while updating options data: {e}"}
    finally:
        data_inputs.db_connection.close_connection()
    return status

if __name__ == "__main__":
    result = run_update_options_data()
    print(result["message"])