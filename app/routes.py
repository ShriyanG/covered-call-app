import time
from datetime import date

from flask import Blueprint, jsonify, render_template, request

from app.src.config.settings import OPTIONS_TICKERS
from app.src.scripts.backtest import run_backtest
from app.src.scripts.get_latest_date import get_latest_dates
from app.src.scripts.predict import predict_daily_options, predict_options
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

# API endpoint to predict daily options
@main.route('/api/daily-options', methods=['POST'])
def daily_options():
    results = predict_daily_options()
    table_results = []
    for r in results:
        table_results.append({
            'ticker': r.get('ticker'),
            'option_type': r.get('option_type'),
            'date': r.get('date', ''),
            'strike_price': r.get('option_strike_price'),
        })
    return jsonify({
        'success': True,
        'message': 'Daily options prediction completed.',
        'results': table_results
    })
@main.route('/update-options')
def update_options():
    return render_template("update_options.html")

# API endpoint for backtest
@main.route('/api/backtest', methods=['POST'])
def api_backtest():
    data = request.get_json()
    ticker = data.get('ticker')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    base_deviation = float(data.get('deviation', 0))
    option_type = data.get('option_type')
    stop_loss = float(data.get('stop_loss', 0))
    results = run_backtest(ticker, start_date, end_date, base_deviation, option_type, stop_loss)
    return jsonify(results)

@main.route('/analyze-performance')
def analyze_performance():
    return render_template("analyze_performance.html", OPTIONS_TICKERS=OPTIONS_TICKERS)
