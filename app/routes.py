from flask import Blueprint, jsonify, render_template, request

# Create a Blueprint for routes
main = Blueprint('main', __name__)

# Home route
@main.route('/')
def home():
    return render_template("index.html")  # Simple HTML page (can be empty for now)

# Predict route
@main.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint to get option predictions.
    Expects JSON input: { "ticker": "AMZN", "option_type": "call" }
    """
    data = request.get_json()
    ticker = data.get('ticker')
    option_type = data.get('option_type')

    if not ticker or not option_type:
        return jsonify({"error": "Missing ticker or option_type"}), 400

    # Placeholder logic
    prediction_result = {
        "ticker": ticker,
        "option_type": option_type,
        "prediction": None,
        "probabilities": None,
        "option_strike_price": None
    }

    # TODO: Call your analysis.predict_option function here
    return jsonify(prediction_result), 200

# Update models route
@main.route('/update-models')
def update_models():
    return render_template("update_models.html")

@main.route('/update-options')
def update_options():
    return render_template("update_options.html")
