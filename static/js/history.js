// StockOptima Prediction History Manager
document.addEventListener("DOMContentLoaded", function() {
    const tableBody = document.getElementById("historyTableBody");
    const tableWrapper = document.getElementById("historyTableWrapper");
    const noHistoryMsg = document.getElementById("noHistoryMessage");
    const searchInput = document.getElementById("historySearchInput");
    const clearBtn = document.getElementById("clearHistoryBtn");
    const trendContainer = document.getElementById("trendChartContainer");
    
    let historyData = [];
    let trendChartInstance = null;

    // Load history from LocalStorage
    function loadHistory() {
        try {
            historyData = JSON.parse(localStorage.getItem("prediction_history") || "[]");
        } catch (e) {
            console.error("Error reading prediction history:", e);
            historyData = [];
        }
    }

    // Save history back to LocalStorage
    function saveHistory() {
        try {
            localStorage.setItem("prediction_history", JSON.stringify(historyData));
        } catch (e) {
            console.error("Error saving prediction history:", e);
        }
    }

    // Render table rows and trend chart
    function render() {
        loadHistory();
        const query = searchInput.value.toLowerCase().trim();
        
        // Filter rows if searching
        const filteredData = historyData.filter(item => {
            return (
                item.productName.toLowerCase().includes(query) ||
                item.category.toLowerCase().includes(query) ||
                item.modelName.toLowerCase().includes(query) ||
                item.recommendation.toLowerCase().includes(query)
            );
        });

        // Toggle empty state message
        if (filteredData.length === 0) {
            if (query === "") {
                tableWrapper.style.display = "none";
                noHistoryMsg.style.display = "block";
                trendContainer.style.display = "none";
            } else {
                tableWrapper.style.display = "block";
                tableBody.innerHTML = `<tr><td colspan="8" class="text-center" style="color: var(--text-secondary); padding: 2rem;">No matching history logs found.</td></tr>`;
            }
            return;
        }

        tableWrapper.style.display = "block";
        noHistoryMsg.style.display = "none";
        
        // Render rows
        tableBody.innerHTML = filteredData.map(item => {
            let recClass = 'rec-maintain';
            if (item.recommendation === 'Reorder Immediately') recClass = 'rec-reorder';
            else if (item.recommendation === 'Increase Stock') recClass = 'rec-increase';
            else if (item.recommendation === 'Reduce Stock') recClass = 'rec-reduce';

            return `
                <tr data-id="${item.id}">
                    <td>${item.date}</td>
                    <td><strong>${item.productName}</strong></td>
                    <td><span style="font-size: 0.8rem; color: var(--text-secondary);">${item.category}</span></td>
                    <td>${item.modelName}</td>
                    <td>${item.currentStock} units</td>
                    <td class="text-success"><strong>${item.predictedDemand} units</strong></td>
                    <td><span class="result-recommendation ${recClass}" style="padding: 0.15rem 0.5rem; font-size: 0.75rem; margin:0;">${item.recommendation}</span></td>
                    <td>
                        <button class="btn-delete" title="Delete Log">
                            <!-- Trash Icon SVG -->
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            </svg>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        // Attach delete events
        const deleteButtons = tableBody.querySelectorAll(".btn-delete");
        deleteButtons.forEach(btn => {
            btn.addEventListener("click", function(e) {
                const tr = e.target.closest("tr");
                const id = tr.getAttribute("data-id");
                deleteItem(id);
            });
        });

        // Render trend chart of predictions (chronological sequence)
        renderTrendChart(filteredData);
    }

    // Delete a single forecast item
    function deleteItem(id) {
        historyData = historyData.filter(item => item.id !== id);
        saveHistory();
        render();
    }

    // Render prediction trend chart
    function renderTrendChart(data) {
        const canvas = document.getElementById("historyTrendChart");
        if (!canvas) return;

        // We only render chart if we have at least 2 points to make a trend
        if (data.length < 2) {
            trendContainer.style.display = "none";
            return;
        }

        trendContainer.style.display = "block";

        // Chart data should be in chronological order (reverse history which is newest first)
        const chronData = [...data].reverse();
        const labels = chronData.map(item => item.productName + ' (' + item.date.split(' ')[1] + ')');
        const demands = chronData.map(item => item.predictedDemand);
        const stocks = chronData.map(item => item.currentStock);

        if (trendChartInstance) {
            trendChartInstance.destroy();
        }

        trendChartInstance = new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Predicted Demand',
                        data: demands,
                        borderColor: '#22c55e',
                        backgroundColor: 'rgba(34, 197, 94, 0.05)',
                        borderWidth: 2,
                        tension: 0.3,
                        pointBackgroundColor: '#22c55e',
                        fill: true
                    },
                    {
                        label: 'Current Stock',
                        data: stocks,
                        borderColor: '#3b82f6',
                        backgroundColor: 'transparent',
                        borderWidth: 1.5,
                        borderDash: [5, 5],
                        tension: 0.3,
                        pointBackgroundColor: '#3b82f6'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#f8fafc', font: { family: 'Inter' } }
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8', font: { family: 'Inter' }, maxRotation: 45, minRotation: 45 }
                    }
                }
            }
        });
    }

    // Search input listener
    if (searchInput) {
        searchInput.addEventListener("input", render);
    }

    // Clear history handler
    if (clearBtn) {
        clearBtn.addEventListener("click", function() {
            if (confirm("Are you sure you want to clear all prediction history? This action cannot be undone.")) {
                historyData = [];
                saveHistory();
                render();
            }
        });
    }

    // Initial render call
    render();
});
