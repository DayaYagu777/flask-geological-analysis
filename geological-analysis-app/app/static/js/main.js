// This file contains JavaScript code for interactive features on the frontend, such as handling user interactions and AJAX requests.

document.addEventListener('DOMContentLoaded', function() {
    // Handle file upload
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(uploadForm);
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('File uploaded successfully!');
                    // Optionally, redirect or update the UI
                } else {
                    alert('File upload failed: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred during file upload.');
            });
        });
    }

    // Initialize data visualization
    const chartContainer = document.getElementById('chart-container');
    if (chartContainer) {
        // Example: Initialize a chart using a library like Chart.js
        const ctx = chartContainer.getContext('2d');
        const myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [], // Populate with your data
                datasets: [{
                    label: 'Geological Data',
                    data: [], // Populate with your data
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Add event listeners for interactive elements
    const filterButton = document.getElementById('filter-button');
    if (filterButton) {
        filterButton.addEventListener('click', function() {
            // Implement filtering logic
            alert('Filter button clicked!');
        });
    }
});