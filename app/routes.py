from datetime import date

from flask import Blueprint, jsonify, render_template, request

# Create a Blueprint for routes
main = Blueprint('main', __name__)

# Home route
@main.route('/')
def home():
    today = date.today().strftime('%B %d, %Y')
    return render_template("dashboard.html", today_date=today)

# Predict route
@main.route('/predict', methods=['GET', 'POST'])
def predict():
    tickers = ['AMZN', 'AAPL', 'GOOG', 'MSFT']  # Example tickers, replace with dynamic source if needed
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

# Update models route
@main.route('/update-models', methods=['POST'])
def update_models():
    # Call your update_models script here
    # Example: from src.update_models import update_models_func
    # result = update_models_func()
    # Simulate long-running task
    import time
    time.sleep(2)  # Remove or replace with actual update logic
    # Return JSON response
    return jsonify({'status': 'Models updated successfully!', 'last_update': date.today().strftime('%B %d, %Y')})

@main.route('/update-options')
def update_options():
    return render_template("update_options.html")

@main.route('/analyze-performance')
def analyze_performance():
    return render_template("analyze_performance.html")
