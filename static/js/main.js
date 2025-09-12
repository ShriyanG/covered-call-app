// Covered Call App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Covered Call App loaded successfully');
    
    // Check API health on page load
    checkAPIHealth();
    
    // Add smooth scrolling for any future navigation
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

// Function to check API health
async function checkAPIHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            console.log('API Health Check: ✅', data.message);
        }
    } catch (error) {
        console.error('API Health Check: ❌', error);
    }
}

// Function to get app status
async function getAppStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching app status:', error);
        return null;
    }
}