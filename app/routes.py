import time
from datetime import date

from flask import Blueprint, jsonify, render_template, request

from app.src.config.settings import OPTIONS_TICKERS
from app.src.scripts.get_latest_date import get_latest_dates
from app.src.scripts.update_models import run_update_models
from app.src.scripts.update_options_data import run_update_options_data
from app.src.scripts.update_stock_data import run_update_stock_data
from app.src.utils.utils import format_date

# Create a Blueprint for routes
main = Blueprint('main', __name__)

# Home route
@main.route('/')
def home():
    today = date.today().strftime('%B %d, %Y')
    latest_date, last_market_day = get_latest_dates()
    formatted_latest = format_date(latest_date)
    formatted_market = format_date(last_market_day)
    return render_template("dashboard.html", today_date=today, latest_date=formatted_latest, last_market_day=formatted_market, tickers=OPTIONS_TICKERS)

# API endpoint to update stock data
@main.route('/api/update-stock-data', methods=['POST'])
def update_stock_data():
    result = run_update_stock_data()
    return jsonify(result)

# API endpoint to update options data
@main.route('/api/update-options-data', methods=['POST'])
def update_options_data():
    result = run_update_options_data()
    return jsonify(result)

# API endpoint to update models
@main.route('/api/update-models', methods=['POST'])
def update_models():
    result = run_update_models()
    latest_date, last_market_day = get_latest_dates()
    formatted_latest = format_date(latest_date)
    formatted_market = format_date(last_market_day)
    result.update({
        'latest_date': formatted_latest,
        'last_market_day': formatted_market
    })
    return jsonify(result)
# Predict route
@main.route('/predict', methods=['GET', 'POST'])
def predict():
    tickers = OPTIONS_TICKERS  # Use the dynamic tickers from settings
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        option_type = request.form.get('option_type')
        # Placeholder prediction logic
        prediction = 'Up' if option_type == 'call' else 'Down'
        # You can update the table data here or return JSON
        return render_template("dashboard.html", today_date=date.today().strftime('%B %d, %Y'), prediction_result={
            'ticker': ticker,
            'option_type': option_type,
            'prediction': prediction
        }, tickers=tickers)
    return render_template("dashboard.html", today_date=date.today().strftime('%B %d, %Y'), tickers=tickers)


@main.route('/update-options')
def update_options():
    return render_template("update_options.html")

@main.route('/analyze-performance')
def analyze_performance():
    return render_template("analyze_performance.html")
