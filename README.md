# Covered Call App

An options trading application that uses models to predict the best stock options for covered calls.

## Features

- **Predictive Models**: Advanced algorithms to analyze market data and predict optimal covered call opportunities
- **Real-time Data**: Access to live market data for informed decision making
- **Risk Management**: Built-in tools to help manage and minimize trading risks

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ShriyanG/covered-call-app.git
   cd covered-call-app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## API Endpoints

- `GET /` - Main application page
- `GET /api/health` - Health check endpoint
- `GET /api/status` - Application status and information

## Project Structure

```
covered-call-app/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   └── index.html     # Homepage template
├── static/            # Static assets
│   ├── css/
│   │   └── style.css  # Application styles
│   ├── js/
│   │   └── main.js    # JavaScript functionality
│   └── images/        # Image assets
└── README.md          # This file
```

## Development

The application is built with Flask and follows standard Flask project structure. The configuration is managed through `config.py` with different environments (development, production, testing).

## License

© 2024 Covered Call App. All rights reserved. 
