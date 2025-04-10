// Get the chart data passed from Flask into the template
const chartData = {{ chart_data | tojson }};

// Set up the chart configuration
const ctx = document.getElementById('conditionChart').getContext('2d');
const conditionChart = new Chart(ctx, {
    type: 'bar',  // Chart type (Bar chart for patient conditions)
    data: {
        labels: chartData.labels,  // Labels for the conditions
        datasets: [{
            label: 'Number of Patients by Condition',
            data: chartData.values,  // Data points (count of patients per condition)
            backgroundColor: 'rgba(75, 192, 192, 0.2)',  // Color for bars
            borderColor: 'rgba(75, 192, 192, 1)',  // Border color for bars
            borderWidth: 1  // Border width
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true  // Start the Y-axis at zero
            }
        }
    }
});
