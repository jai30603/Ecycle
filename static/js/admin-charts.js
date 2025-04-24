// Admin dashboard charts functionality

function createAdminDashboardCharts(pickupData, userData, ewasteData) {
    // Pickups chart - stacked bar chart showing pending vs completed pickups
    if (document.getElementById('pickupsChart')) {
        const pickupsCtx = document.getElementById('pickupsChart').getContext('2d');
        
        new Chart(pickupsCtx, {
            type: 'bar',
            data: {
                labels: pickupData.labels,
                datasets: [{
                    label: 'Pending Pickups',
                    data: pickupData.pending,
                    backgroundColor: '#ffc107',
                    borderColor: '#e0a800',
                    borderWidth: 1
                }, {
                    label: 'Completed Pickups',
                    data: pickupData.completed,
                    backgroundColor: '#20c997',
                    borderColor: '#1ba87e',
                    borderWidth: 1
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
    
    // User registration chart - line chart showing user growth
    if (document.getElementById('userRegistrationChart')) {
        const userCtx = document.getElementById('userRegistrationChart').getContext('2d');
        
        // Create gradient fill
        const gradientFill = userCtx.createLinearGradient(0, 0, 0, 300);
        gradientFill.addColorStop(0, 'rgba(13, 110, 253, 0.7)');
        gradientFill.addColorStop(1, 'rgba(13, 110, 253, 0.1)');
        
        new Chart(userCtx, {
            type: 'line',
            data: {
                labels: userData.labels,
                datasets: [{
                    label: 'New Users',
                    data: userData.counts,
                    borderColor: '#0d6efd',
                    backgroundColor: gradientFill,
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#0d6efd',
                    pointRadius: 4,
                    pointHoverRadius: 6
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
    
    // E-waste types chart - polar area chart showing distribution of e-waste types
    if (document.getElementById('ewasteTypesAdminChart')) {
        const ewasteCtx = document.getElementById('ewasteTypesAdminChart').getContext('2d');
        
        new Chart(ewasteCtx, {
            type: 'polarArea',
            data: {
                labels: ewasteData.labels,
                datasets: [{
                    data: ewasteData.counts,
                    backgroundColor: [
                        '#20c997', '#0dcaf0', '#6610f2', '#fd7e14', '#dc3545', '#0d6efd'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 10
                        }
                    }
                }
            }
        });
    }
}

// Function to create time-series chart for admin analytics
function createTimeSeriesChart(elementId, data, options = {}) {
    if (!document.getElementById(elementId)) return;
    
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Default options
    const defaultOptions = {
        type: 'line',
        fill: false,
        borderColor: '#0dcaf0',
        tension: 0.3
    };
    
    // Merge options
    const chartOptions = {...defaultOptions, ...options};
    
    // Create dataset
    const dataset = {
        label: chartOptions.label || 'Data',
        data: data.values,
        borderColor: chartOptions.borderColor,
        backgroundColor: chartOptions.backgroundColor || chartOptions.borderColor,
        tension: chartOptions.tension,
        fill: chartOptions.fill
    };
    
    // If fill is true and no backgroundColor specified, create gradient
    if (chartOptions.fill && !chartOptions.backgroundColor) {
        const gradientFill = ctx.createLinearGradient(0, 0, 0, 300);
        gradientFill.addColorStop(0, `${chartOptions.borderColor}70`);  // 70 = 44% opacity
        gradientFill.addColorStop(1, `${chartOptions.borderColor}10`);  // 10 = 6% opacity
        dataset.backgroundColor = gradientFill;
    }
    
    // Create chart configuration
    const config = {
        type: chartOptions.type,
        data: {
            labels: data.labels,
            datasets: [dataset]
        },
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
                        precision: chartOptions.precision || 0
                    }
                }
            }
        }
    };
    
    return new Chart(ctx, config);
}

// Function to create bar chart for comparing values
function createBarComparisonChart(elementId, data, options = {}) {
    if (!document.getElementById(elementId)) return;
    
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Default colors
    const defaultColors = [
        '#20c997', '#0dcaf0', '#6610f2', '#fd7e14', '#dc3545',
        '#0d6efd', '#6f42c1', '#d63384', '#ffc107', '#198754'
    ];
    
    // Create chart configuration
    const config = {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: options.label || 'Data',
                data: data.values,
                backgroundColor: options.colors || defaultColors.slice(0, data.labels.length)
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: options.showLegend !== false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: options.precision || 0
                    }
                }
            }
        }
    };
    
    return new Chart(ctx, config);
}
