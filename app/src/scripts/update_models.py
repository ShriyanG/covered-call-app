from app.src.analysis import Analysis
from app.src.config.settings import FEATURES, TICKERS


def run_update_models():
    analysis = Analysis()
    try:
        for ticker in TICKERS:
            analysis.update_models(ticker, FEATURES)
        status = {"success": True, "message": "Model and features for all tickers updated and saved."}
    except Exception as e:
        status = {"success": False, "message": f"An error occurred while updating models: {e}"}
    return status

if __name__ == "__main__":
    result = run_update_models()
    print(result["message"])