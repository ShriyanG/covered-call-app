document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('backtest-form');
    const loadingDiv = document.getElementById('backtest-loading');
    const resultsDiv = document.getElementById('backtest-results');
    const chartCanvas = document.getElementById('backtest-chart');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        resultsDiv.innerHTML = '';
        if (chartCanvas) {
            chartCanvas.style.display = 'none';
        }

        // Input validation: start date must not be after end date, end date must not be after today, start date must not be before May 10, 2023
        const startDate = form.start_date.value;
        const endDate = form.end_date.value;
        const today = new Date();
        const todayStr = today.toISOString().slice(0, 10); // 'YYYY-MM-DD'
        const minDate = '2023-05-10';

        if (startDate < minDate) {
            resultsDiv.innerHTML = `<div style=\"color:red; font-weight:bold;\">Start date cannot be before May 10, 2023.</div>`;
            return;
        }
        if (startDate > endDate) {
            resultsDiv.innerHTML = '<div style="color:red; font-weight:bold;">Start date cannot be after end date.</div>';
            return;
        }
        if (endDate > todayStr) {
            resultsDiv.innerHTML = `<div style="color:red; font-weight:bold;">End date cannot be after today's date (${todayStr}).</div>`;
            return;
        }

        loadingDiv.style.display = 'block';

        // Gather form data
        const formData = {
            ticker: form.ticker.value,
            start_date: startDate,
            end_date: endDate,
            option_type: form.option_type.value,
            deviation: form.deviation.value,
            stop_loss: form.stop_loss.value
        };

        // Send POST request to backend
        let response = await fetch('/api/backtest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        let results = await response.json();

        // Display results
        resultsDiv.innerHTML = `
            <h3>Backtest Results</h3>
            <ul>
                <li><strong>Total Profit:</strong> $${results.total_profit}</li>
                <li><strong>Total Trades:</strong> ${results.total_trades}</li>
                <li><strong>Successful Trades:</strong> ${results.successful_trades}</li>
                <li><strong>Stop Losses Hit:</strong> ${results.stop_losses_hit}</li>
                <li><strong>Negative Trades:</strong> ${results.negative_trades}</li>
                <li><strong>Neutral Trades:</strong> ${results.neutral_trades}</li>
                <li><strong>Success Rate:</strong> ${results.success_rate}%</li>
                <li><strong>Avg Gain per Successful Trade:</strong> $${results.avg_gain_per_successful_trade}</li>
            </ul>
        `;

        // Display chart
        chartCanvas.style.display = 'block';
        const ctx = chartCanvas.getContext('2d');
        let profit_curve = results.profit_curve || [];
        let labels = profit_curve.length > 1 ? [profit_curve[0].date, profit_curve[profit_curve.length-1].date] : profit_curve.map(p => p.date);
        let data = profit_curve.length > 1 ? [profit_curve[0].profit, profit_curve[profit_curve.length-1].profit] : profit_curve.map(p => p.profit);
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Profit Curve',
                    data: data,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0,123,255,0.1)',
                    fill: true,
                    tension: 0.2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'Profit Over Time' }
                },
                scales: {
                    x: { title: { display: true, text: 'Date' } },
                    y: { title: { display: true, text: 'Profit ($)' } }
                }
            }
        });

        loadingDiv.style.display = 'none';
    });
});
