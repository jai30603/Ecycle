// Charts.js file for dashboard visualizations

// Create user dashboard chart
function createUserStatsChart(elementId, data) {
    if (!document.getElementById(elementId)) return;
    
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Create gradient fill
    const gradientFill = ctx.createLinearGradient(0, 0, 0, 400);
    gradientFill.addColorStop(0, 'rgba(32, 201, 151, 0.6)');
    gradientFill.addColorStop(1, 'rgba(32, 201, 151, 0)');
    
    const chartData = {
        labels: data.labels,
        datasets: [{
            label: 'Eco Points Earned',
            data: data.ecoPoints,
            borderColor: '#20c997',
            backgroundColor: gradientFill,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: '#20c997',
            pointRadius: 4,
            pointHoverRadius: 6
        }]
    };
    
    const config = {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    };
    
    return new Chart(ctx, config);
}

// Create e-waste type distribution chart
function createEwasteTypesChart(elementId, data) {
    if (!document.getElementById(elementId)) return;
    
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const chartData = {
        labels: data.labels,
        datasets: [{
            label: 'Number of Items',
            data: data.counts,
            backgroundColor: [
                '#20c997', '#0dcaf0', '#6610f2', '#fd7e14', '#dc3545',
                '#0d6efd', '#6f42c1', '#d63384', '#ffc107', '#198754'
            ],
            hoverOffset: 4
        }]
    };
    
    const config = {
        type: 'doughnut',
        data: chartData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    };
    
    return new Chart(ctx, config);
}

// Create admin dashboard charts
function createAdminDashboardCharts(pickupData, userData, ewasteData) {
    // Pickups chart
    if (document.getElementById('pickupsChart')) {
        const pickupsCtx = document.getElementById('pickupsChart').getContext('2d');
        
        const pickupsChart = new Chart(pickupsCtx, {
            type: 'bar',
            data: {
                labels: pickupData.labels,
                datasets: [{
                    label: 'Pending Pickups',
                    data: pickupData.pending,
                    backgroundColor: '#ffc107'
                }, {
                    label: 'Completed Pickups',
                    data: pickupData.completed,
                    backgroundColor: '#20c997'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        stacked: true
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    // User registration chart
    if (document.getElementById('userRegistrationChart')) {
        const userCtx = document.getElementById('userRegistrationChart').getContext('2d');
        
        const userChart = new Chart(userCtx, {
            type: 'line',
            data: {
                labels: userData.labels,
                datasets: [{
                    label: 'New Users',
                    data: userData.counts,
                    borderColor: '#0dcaf0',
                    backgroundColor: 'rgba(13, 202, 240, 0.2)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    // E-waste types chart
    if (document.getElementById('ewasteTypesAdminChart')) {
        const ewasteCtx = document.getElementById('ewasteTypesAdminChart').getContext('2d');
        
        const ewasteChart = new Chart(ewasteCtx, {
            type: 'polarArea',
            data: {
                labels: ewasteData.labels,
                datasets: [{
                    data: ewasteData.counts,
                    backgroundColor: [
                        '#20c997', '#0dcaf0', '#6610f2', '#fd7e14', '#dc3545',
                        '#0d6efd', '#6f42c1', '#d63384', '#ffc107', '#198754'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                    }
                }
            }
        });
    }
}

// Create carbon savings chart
function createCarbonSavingsChart(elementId, data) {
    if (!document.getElementById(elementId)) return;
    
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const chartData = {
        labels: data.labels,
        datasets: [{
            label: 'Carbon Saved (kg CO2)',
            data: data.values,
            borderColor: '#198754',
            backgroundColor: 'rgba(25, 135, 84, 0.2)',
            tension: 0.4,
            fill: true
        }]
    };
    
    const config = {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    };
    
    return new Chart(ctx, config);
}
