// StockOptima Dashboard Chart Rendering
document.addEventListener("DOMContentLoaded", function() {
    // 1. Current Stock vs Predicted Demand by Category Chart
    const ctxCategory = document.getElementById('categoryStockChart');
    if (ctxCategory && typeof categoryLabels !== 'undefined') {
        new Chart(ctxCategory.getContext('2d'), {
            type: 'bar',
            data: {
                labels: categoryLabels,
                datasets: [
                    {
                        label: 'Current Stock',
                        data: categoryStocks,
                        backgroundColor: 'rgba(59, 130, 246, 0.4)', // Accent Blue
                        borderColor: '#3b82f6',
                        borderWidth: 1.5,
                        borderRadius: 6
                    },
                    {
                        label: 'Predicted Demand',
                        data: categoryDemands,
                        backgroundColor: 'rgba(34, 197, 94, 0.4)', // Success Green
                        borderColor: '#22c55e',
                        borderWidth: 1.5,
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#f8fafc',
                            font: { family: 'Inter', size: 12 }
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#f8fafc',
                        bodyColor: '#f8fafc',
                        borderColor: 'rgba(255,255,255,0.08)',
                        borderWidth: 1
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                    }
                }
            }
        });
    }

    // 2. Model R2 validation comparison chart (Horizontal Bar Chart)
    const ctxR2 = document.getElementById('modelR2Chart');
    if (ctxR2 && typeof modelNames !== 'undefined') {
        // Map R2 values to percentages for displays
        const r2Percentages = modelR2s.map(val => val * 100);
        
        new Chart(ctxR2.getContext('2d'), {
            type: 'bar',
            data: {
                labels: modelNames,
                datasets: [{
                    label: 'R² Score (%)',
                    data: r2Percentages,
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.45)', // RF
                        'rgba(16, 185, 129, 0.45)', // GB
                        'rgba(245, 158, 11, 0.45)'  // DT
                    ],
                    borderColor: [
                        '#3b82f6',
                        '#10b981',
                        '#f59e0b'
                    ],
                    borderWidth: 1.5,
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y', // Renders horizontally
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#f8fafc',
                        bodyColor: '#f8fafc',
                        callbacks: {
                            label: function(context) {
                                return `Accuracy: ${context.parsed.x.toFixed(2)}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        min: 80,
                        max: 100,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8', font: { family: 'Inter', weight: 'bold' } }
                    }
                }
            }
        });
    }
});
