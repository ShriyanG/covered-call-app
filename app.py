"""
Covered Call App - Options Trading Application
Main Flask application entry point
"""

from flask import Flask, render_template, jsonify

# Create Flask application instance
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
app.config['DEBUG'] = True  # Set to False in production

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'message': 'Covered Call App is running'
    })

@app.route('/api/status')
def status():
    """Status endpoint with basic app information"""
    return jsonify({
        'app_name': 'Covered Call App',
        'description': 'Options trading application that uses models to predict best stock options for covered calls',
        'version': '1.0.0',
        'status': 'running'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)