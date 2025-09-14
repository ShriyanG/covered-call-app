// main.js - For dynamic AJAX/Javascript functions

// Spinner, alert, and last update for prediction form
function setupPredictForm() {
    const predictForm = document.getElementById('predict-form');
    if (predictForm) {
        predictForm.onsubmit = function(e) {
            document.getElementById('spinner').style.display = 'block';
        };
    }
}

// Log message styling and spinner
function appendLog(message, type = '') {
    const logDiv = document.getElementById('log');
    const div = document.createElement('div');
    div.className = type;
    div.innerHTML = message;
    logDiv.appendChild(div);
}

// AJAX for Update Models with live progress log
function setupUpdateModels() {
    const updateBtn = document.getElementById('update-models-btn');
    if (updateBtn) {
        updateBtn.onclick = async function() {
            document.getElementById('spinner').style.display = 'block';
            const logDiv = document.getElementById('log');
            logDiv.innerHTML = '';

            // Step 1: Update stock data
            appendLog('Updating stock data table...', 'step');
            let stockRes = await fetch('/api/update-stock-data', { method: 'POST' });
            let stockData = await stockRes.json();
            appendLog(stockData.message, stockData.success ? 'success' : 'error');

            // Step 2: Update option data
            appendLog('Updating option data table...', 'step');
            let optionsRes = await fetch('/api/update-options-data', { method: 'POST' });
            let optionsData = await optionsRes.json();
            appendLog(optionsData.message, optionsData.success ? 'success' : 'error');

            // Step 3: Update models
            appendLog('Updating models...', 'step');
            let modelsRes = await fetch('/api/update-models', { method: 'POST' });
            let modelsData = await modelsRes.json();
            appendLog(modelsData.message, modelsData.success ? 'success' : 'error');

            document.getElementById('spinner').style.display = 'none';
            document.getElementById('alert').style.display = 'block';
            document.getElementById('alert').textContent = modelsData.message;

            // Update dashboard status and dates
            setModelStatus(modelsData.latest_date, modelsData.last_market_day);

            setTimeout(() => { logDiv.innerHTML = ''; }, 2000); // Hide log after 2 seconds
        };
    }
}

// Set model status based on date comparison
function setModelStatus(latestDate, lastMarketDay) {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.status');
    const normLatest = latestDate ? latestDate.trim() : '';
    const normMarket = lastMarketDay ? lastMarketDay.trim() : '';
    if (statusIndicator && statusText) {
        if (normLatest === normMarket) {
            statusIndicator.style.background = '#4caf50'; // green
            statusText.innerHTML = '<span class="status-indicator" style="background:#4caf50;"></span> Model Status: <span style="color:#4caf50;font-weight:bold;">Up-to-date</span> | Latest Trading Data: <span id="last-update">' + normLatest + '</span>';
        } else {
            statusIndicator.style.background = '#d32f2f'; // red
            statusText.innerHTML = '<span class="status-indicator" style="background:#d32f2f;"></span> Model Status: <span style="color:#d32f2f;font-weight:bold;">Outdated</span> | Latest Trading Data: <span id="last-update">' + normLatest + '</span>';
        }
    }
}

// Initialize all functions
function initializeDashboard() {
    setupPredictForm();
    setupUpdateModels();
    // You need to pass latestDate and lastMarketDay from backend via template variables
    const latestDate = document.getElementById('last-update')?.textContent;
    const lastMarketDay = document.getElementById('last-market-day')?.textContent;
    if (latestDate && lastMarketDay) {
        setModelStatus(latestDate, lastMarketDay);
    }
}

document.addEventListener('DOMContentLoaded', initializeDashboard);
