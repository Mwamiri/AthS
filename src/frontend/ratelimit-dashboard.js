// Rate Limit Dashboard Component
// Real-time view of API usage and quota

class RateLimitDashboard {
    constructor() {
        this.container = document.getElementById('ratelimit-dashboard');
        this.apiBase = '/api/dashboard/ratelimit';
        this.refreshInterval = 5000; // Refresh every 5 seconds
        this.init();
    }

    init() {
        if (!this.container) {
            console.warn('Rate limit dashboard container not found');
            return;
        }

        this.render();
        this.startAutoRefresh();
    }

    render() {
        this.container.innerHTML = `
            <div class="ratelimit-dashboard">
                <div class="dashboard-header">
                    <h2>📊 Rate Limit Dashboard</h2>
                    <button class="btn-refresh" onclick="rateLimitDashboard.refresh()">Refresh</button>
                </div>

                <div class="dashboard-grid">
                    <!-- User Tier Card -->
                    <div class="card tier-card">
                        <h3>Your Quota</h3>
                        <div class="tier-info" id="tier-info">
                            <p>Loading...</p>
                        </div>
                    </div>

                    <!-- Global Stats Card -->
                    <div class="card stats-card">
                        <h3>📈 Global Statistics</h3>
                        <div class="stats-content" id="global-stats">
                            <p>Loading...</p>
                        </div>
                    </div>

                    <!-- Usage by Endpoint -->
                    <div class="card endpoints-card">
                        <h3>🔗 Top Endpoints</h3>
                        <div class="endpoints-list" id="endpoints-list">
                            <p>Loading...</p>
                        </div>
                    </div>

                    <!-- Usage Chart -->
                    <div class="card chart-card">
                        <h3>📉 Usage Trend</h3>
                        <div class="chart-container" id="usage-chart">
                            <canvas id="usage-canvas"></canvas>
                        </div>
                    </div>
                </div>

                <div class="dashboard-footer">
                    <p>Last updated: <span id="last-updated">--:--:--</span></p>
                    <p class="info-text">💡 Tip: Upgrade to Pro tier for higher limits</p>
                </div>
            </div>
        `;

        // Fetch and display data
        this.loadDashboardData();
    }

    async loadDashboardData() {
        const userId = this.getUserId();

        try {
            // Load user tier
            const tierRes = await fetch(`${this.apiBase}/user/${userId}/tier`);
            const tierData = await tierRes.json();
            this.displayTierInfo(tierData);

            // Load global stats
            const globRes = await fetch(`${this.apiBase}/global`);
            const globData = await globRes.json();
            this.displayGlobalStats(globData);

            // Load endpoint stats
            const endRes = await fetch(`${this.apiBase}/user/${userId}`);
            const endData = await endRes.json();
            this.displayEndpoints(endData);

            // Update timestamp
            document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    }

    displayTierInfo(data) {
        const container = document.getElementById('tier-info');
        const percentUsed = data.percentage_used.toFixed(1);
        const remaining = Math.max(0, data.remaining);

        const tierColor = percentUsed > 80 ? '#e63946' : percentUsed > 50 ? '#f7931e' : '#06d6a0';

        container.innerHTML = `
            <div class="tier-details">
                <div class="tier-badge" style="background: ${tierColor};">
                    <strong>${data.tier.toUpperCase()}</strong>
                </div>

                <div class="quota-info">
                    <p><strong>Hourly Limit:</strong> ${data.limits.requests_per_hour.toLocaleString()}</p>
                    <p><strong>Daily Limit:</strong> ${data.limits.requests_per_day.toLocaleString()}</p>
                </div>

                <div class="usage-bar">
                    <div class="progress-bar" style="width: ${percentUsed}%; background: ${tierColor};"></div>
                    <span class="usage-text">${percentUsed}% used</span>
                </div>

                <div class="quota-stats">
                    <p>📊 Current Usage: <strong>${data.current_usage}</strong> / ${data.limits.requests_per_hour}</p>
                    <p>✅ Remaining: <strong>${remaining}</strong></p>
                </div>
            </div>
        `;
    }

    displayGlobalStats(data) {
        const container = document.getElementById('global-stats');

        container.innerHTML = `
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-label">Total Requests</span>
                    <span class="stat-value">${data.total_requests.toLocaleString()}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Active Users</span>
                    <span class="stat-value">${data.unique_users}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Endpoints</span>
                    <span class="stat-value">${data.endpoints_tracked}</span>
                </div>
            </div>

            ${data.top_endpoints.length > 0 ? `
                <div class="top-endpoints-mini">
                    <p><strong>Most Used Endpoints:</strong></p>
                    <ul>
                        ${data.top_endpoints.slice(0, 3).map(ep => `
                            <li>${ep.endpoint}: ${ep.requests} requests</li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
    }

    displayEndpoints(data) {
        const container = document.getElementById('endpoints-list');

        if (Object.keys(data.by_endpoint).length === 0) {
            container.innerHTML = '<p>No API calls yet</p>';
            return;
        }

        const endpoints = Object.entries(data.by_endpoint)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);

        const maxCount = Math.max(...endpoints.map(e => e[1]));

        container.innerHTML = endpoints.map(([endpoint, count]) => {
            const percent = (count / maxCount) * 100;
            return `
                <div class="endpoint-item">
                    <span class="endpoint-name">${endpoint}</span>
                    <div class="endpoint-bar">
                        <div class="endpoint-usage" style="width: ${percent}%"></div>
                    </div>
                    <span class="endpoint-count">${count}</span>
                </div>
            `;
        }).join('');
    }

    async refresh() {
        await this.loadDashboardData();
    }

    startAutoRefresh() {
        setInterval(() => this.refresh(), this.refreshInterval);
    }

    getUserId() {
        // Get user ID from auth or localStorage
        return window.authStore?.userId || localStorage.getItem('user_id') || 1;
    }
}

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    window.rateLimitDashboard = new RateLimitDashboard();
});


// ============================================
// Styles for Rate Limit Dashboard
// ============================================
const dashboardStyles = `
<style>
.ratelimit-dashboard {
    padding: 20px;
    background: var(--bg-secondary, #f5f5f5);
    border-radius: 12px;
}

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.dashboard-header h2 {
    margin: 0;
    font-size: 24px;
}

.btn-refresh {
    padding: 8px 16px;
    background: #06d6a0;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
}

.btn-refresh:hover {
    background: #05b889;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card h3 {
    margin-top: 0;
    color: #333;
}

.tier-badge {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 20px;
    color: white;
    font-weight: bold;
    margin-bottom: 15px;
}

.quota-info {
    margin-bottom: 15px;
}

.quota-info p {
    margin: 8px 0;
    font-size: 14px;
}

.progress-bar {
    height: 8px;
    background: #e63946;
    border-radius: 4px;
    margin: 10px 0;
}

.usage-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 15px;
}

.usage-bar .progress-bar {
    flex: 1;
    margin: 0;
}

.usage-text {
    font-size: 12px;
    white-space: nowrap;
}

.quota-stats p {
    margin: 6px 0;
    font-size: 13px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 15px;
}

.stat-item {
    text-align: center;
    padding: 15px;
    background: #f9f9f9;
    border-radius: 6px;
}

.stat-label {
    display: block;
    font-size: 12px;
    color: #666;
    margin-bottom: 5px;
}

.stat-value {
    display: block;
    font-size: 24px;
    font-weight: bold;
    color: #06d6a0;
}

.top-endpoints-mini ul {
    list-style: none;
    padding: 0;
}

.top-endpoints-mini li {
    padding: 5px 0;
    font-size: 12px;
    color: #666;
}

.endpoint-item {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}

.endpoint-name {
    min-width: 120px;
    font-size: 12px;
    font-weight: 500;
}

.endpoint-bar {
    flex: 1;
    height: 6px;
    background: #e0e0e0;
    border-radius: 3px;
    overflow: hidden;
}

.endpoint-usage {
    height: 100%;
    background: #06d6a0;
}

.endpoint-count {
    min-width: 30px;
    text-align: right;
    font-size: 12px;
    font-weight: 500;
}

.dashboard-footer {
    text-align: center;
    padding-top: 20px;
    border-top: 1px solid #eee;
    font-size: 12px;
    color: #666;
}

.info-text {
    color: #f7931e;
    margin: 5px 0;
}
</style>
`;

// Inject styles
if (document.head) {
    const style = document.createElement('div');
    style.innerHTML = dashboardStyles;
    document.head.appendChild(style);
}
