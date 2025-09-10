/**
 * Scoreboard functionality for DCTFd
 * Provides real-time updates and visualizations for the scoreboard
 */

// Initialize the scoreboard
document.addEventListener('DOMContentLoaded', function() {
    initScoreboard();
    setupRefreshButton();
    setupCategoryFilter();
    setupGraphToggle();
});

/**
 * Initialize the scoreboard functionality
 */
function initScoreboard() {
    const scoreboard = document.getElementById('scoreboard-table');
    if (!scoreboard) return;
    
    // Add animation classes to entries
    const entries = scoreboard.querySelectorAll('tbody tr');
    entries.forEach((entry, index) => {
        entry.classList.add('scoreboard-entry');
        entry.style.animationDelay = `${index * 0.05}s`;
    });
    
    // Highlight current user/team
    highlightCurrentEntry();
    
    // Initialize the score graph if it exists
    initScoreGraph();
}

/**
 * Highlight the current user or team in the scoreboard
 */
function highlightCurrentEntry() {
    const currentId = document.getElementById('scoreboard-table').dataset.currentId;
    if (!currentId) return;
    
    const entries = document.querySelectorAll('.scoreboard-entry');
    entries.forEach(entry => {
        if (entry.dataset.id === currentId) {
            entry.classList.add('current-entry');
            
            // Scroll to current entry
            entry.scrollIntoView({ block: 'center', behavior: 'smooth' });
        }
    });
}

/**
 * Initialize the score graph visualization
 */
function initScoreGraph() {
    const graphContainer = document.getElementById('score-graph');
    if (!graphContainer) return;
    
    // Check if data attribute exists
    const scoreData = graphContainer.dataset.scores;
    if (!scoreData) {
        console.error('No score data available for graph');
        graphContainer.innerHTML = '<div class="alert alert-info">No score data available for graph.</div>';
        return;
    }
    
    try {
        const data = JSON.parse(scoreData);
        
        // Check if data is empty
        if (Object.keys(data).length === 0) {
            graphContainer.innerHTML = '<div class="alert alert-info">No score data available yet. Complete challenges to see your progress!</div>';
            return;
        }
        
        renderScoreGraph(graphContainer, data);
    } catch (e) {
        console.error('Error parsing score data:', e);
        graphContainer.innerHTML = '<div class="alert alert-danger">Error processing score data: ' + e.message + '</div>';
    }
}

/**
 * Render the score graph with the provided data
 */
function renderScoreGraph(container, data) {
    // Create a canvas for Chart.js
    const canvas = document.createElement('canvas');
    canvas.id = 'scoreChartCanvas';
    container.appendChild(canvas);
    
    // Extract data for the chart
    const datasets = [];
    
    // Set up colors for different teams/users
    const colors = [
        '#4285F4', '#EA4335', '#FBBC05', '#34A853', // Google colors
        '#3B5998', '#8B9DC3', '#DFE3EE', '#F7F7F7', // Facebook colors
        '#1DA1F2', '#AAB8C2', '#E1E8ED', '#FFFFFF', // Twitter colors
        '#7289DA', '#99AAB5', '#2C2F33', '#23272A'  // Discord colors
    ];
    
    // Get event start time
    let eventStart = parseInt(container.dataset.eventStart || '0') * 1000;
    if (!eventStart) {
        // If no event start, use the earliest timestamp
        const timestamps = Object.keys(data).map(ts => parseInt(ts));
        if (timestamps.length > 0) {
            eventStart = Math.min(...timestamps) * 1000;
        } else {
            eventStart = Date.now() - (24 * 60 * 60 * 1000); // Default to 24 hours ago
        }
    }
    
    // Process data for the chart
    try {
        if (typeof data === 'object' && !Array.isArray(data)) {
            // Get all team/user names
            const participants = new Set();
            Object.values(data).forEach(timestampData => {
                Object.keys(timestampData).forEach(name => participants.add(name));
            });
            
            // Create dataset for each team/user
            Array.from(participants).forEach((name, idx) => {
                const color = colors[idx % colors.length];
                const scoreData = [];
                
                // Convert timestamps to data points
                Object.keys(data).sort((a, b) => parseInt(a) - parseInt(b)).forEach(ts => {
                    const timestamp = parseInt(ts);
                    const score = data[ts][name] || null;
                    
                    if (score !== null) {
                        scoreData.push({
                            x: new Date(eventStart + (timestamp * 1000)),
                            y: score
                        });
                    }
                });
                
                if (scoreData.length > 0) {
                    datasets.push({
                        label: name,
                        data: scoreData,
                        borderColor: color,
                        backgroundColor: color + '20',
                        fill: false,
                        tension: 0.1,
                        pointRadius: 2,
                        pointHoverRadius: 5
                    });
                }
            });
        } else if (Array.isArray(data)) {
            // If data is already in datasets format
            datasets.push(...data);
        }
    } catch (e) {
        console.error('Error processing chart data:', e);
        container.innerHTML = '<div class="alert alert-danger">Error processing chart data: ' + e.message + '</div>';
        return;
    }
    
    // Check if we have any datasets
    if (datasets.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No score data available yet.</div>';
        return;
    }
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        // Load Chart.js dynamically
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        script.onload = function() {
            // Also load the date adapter
            const adapterScript = document.createElement('script');
            adapterScript.src = 'https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns';
            adapterScript.onload = function() {
                createChart(canvas, datasets);
            };
            document.head.appendChild(adapterScript);
        };
        document.head.appendChild(script);
    } else {
        createChart(canvas, datasets);
    }
}

/**
 * Create the Chart.js chart
 */
function createChart(canvas, datasets) {
    new Chart(canvas, {
        type: 'line',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'nearest',
                intersect: false
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'hour',
                        displayFormats: {
                            hour: 'MMM d, HH:mm'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Score'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function(tooltipItems) {
                            if (tooltipItems.length > 0) {
                                const date = new Date(tooltipItems[0].parsed.x);
                                return date.toLocaleString();
                            }
                            return '';
                        }
                    }
                },
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

/**
 * Set up the refresh button for the scoreboard
 */
function setupRefreshButton() {
    const refreshBtn = document.getElementById('refresh-scoreboard');
    if (!refreshBtn) return;
    
    refreshBtn.addEventListener('click', function() {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="fas fa-sync fa-spin"></i> Refreshing...';
        
        // Fetch the updated scoreboard data
        fetch(window.location.href)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                
                // Replace the scoreboard table
                const newTable = doc.getElementById('scoreboard-table');
                const currentTable = document.getElementById('scoreboard-table');
                
                if (newTable && currentTable) {
                    currentTable.innerHTML = newTable.innerHTML;
                    initScoreboard();
                }
                
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh';
            })
            .catch(error => {
                console.error('Error refreshing scoreboard:', error);
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh';
            });
    });
}

/**
 * Set up category filtering for the scoreboard
 */
function setupCategoryFilter() {
    const filterSelect = document.getElementById('category-filter');
    if (!filterSelect) return;
    
    filterSelect.addEventListener('change', function() {
        const category = this.value;
        const rows = document.querySelectorAll('.scoreboard-entry');
        
        rows.forEach(row => {
            if (category === 'all' || row.dataset.category === category) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

/**
 * Set up the graph toggle button
 */
function setupGraphToggle() {
    const toggleBtn = document.getElementById('toggle-graph');
    if (!toggleBtn) return;
    
    toggleBtn.addEventListener('click', function() {
        const graphContainer = document.getElementById('score-graph-container');
        if (!graphContainer) return;
        
        if (graphContainer.classList.contains('d-none')) {
            graphContainer.classList.remove('d-none');
            toggleBtn.innerHTML = '<i class="fas fa-chart-line"></i> Hide Graph';
            
            // Initialize graph if it hasn't been created yet
            if (!document.getElementById('scoreChartCanvas')) {
                initScoreGraph();
            }
        } else {
            graphContainer.classList.add('d-none');
            toggleBtn.innerHTML = '<i class="fas fa-chart-line"></i> Show Graph';
        }
    });
    
    // Set up timeframe buttons
    const timeframeButtons = document.querySelectorAll('[data-timeframe]');
    timeframeButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all timeframe buttons
            timeframeButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Get the selected timeframe
            const timeframe = this.dataset.timeframe;
            
            // Apply timeframe filter to graph
            applyTimeframeFilter(timeframe);
        });
    });
}

/**
 * Apply timeframe filter to the graph
 */
function applyTimeframeFilter(timeframe) {
    const chart = Chart.getChart('scoreChartCanvas');
    if (!chart) return;
    
    const now = new Date();
    let minTime = null;
    
    switch(timeframe) {
        case 'hour':
            minTime = new Date(now.getTime() - (60 * 60 * 1000)); // 1 hour ago
            break;
        case 'day':
            minTime = new Date(now.getTime() - (24 * 60 * 60 * 1000)); // 24 hours ago
            break;
        case 'all':
        default:
            minTime = null;
            break;
    }
    
    // Update chart min time
    if (minTime) {
        chart.options.scales.x.min = minTime;
    } else {
        delete chart.options.scales.x.min;
    }
    
    chart.update();
}
