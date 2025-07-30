// Bot Monitoring JavaScript
class BotMonitor {
    constructor() {
        this.logContainer = document.getElementById('bot-logs-container');
        this.logCount = document.getElementById('log-count');
        this.lastLogId = 0;
        this.autoRefresh = true;
        this.refreshInterval = 5000; // 5 seconds
        
        this.init();
    }
    
    init() {
        // Load initial logs
        this.loadLogs();
        
        // Set up auto-refresh
        setInterval(() => {
            if (this.autoRefresh) {
                this.loadLogs();
            }
        }, this.refreshInterval);
        
        // Add event listeners
        this.addEventListeners();
    }
    
    addEventListeners() {
        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                this.autoRefresh = e.target.checked;
                if (this.autoRefresh) {
                    this.showNotification('Auto-refresh enabled', 'info');
                } else {
                    this.showNotification('Auto-refresh disabled', 'info');
                }
            });
        }
        
        // Clear logs button
        const clearLogsBtn = document.getElementById('clear-logs-btn');
        if (clearLogsBtn) {
            clearLogsBtn.addEventListener('click', () => {
                this.clearLogs();
            });
        }
        
        // Manual refresh button
        const refreshBtn = document.getElementById('refresh-logs-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadLogs();
            });
        }
    }
    
    async loadLogs() {
        try {
            const response = await fetch('/api/bot-logs/');
            const data = await response.json();
            
            if (data.success) {
                this.updateLogsDisplay(data.logs);
                this.updateLogCount(data.total_logs);
            } else {
                console.error('Failed to load logs:', data.error);
            }
        } catch (error) {
            console.error('Error loading logs:', error);
        }
    }
    
    updateLogsDisplay(logs) {
        if (!this.logContainer) return;
        
        let html = '';
        
        logs.forEach(log => {
            const logClass = this.getLogClass(log.log_type);
            const icon = this.getLogIcon(log.log_type);
            const timestamp = this.formatTimestamp(log.timestamp);
            
            html += `
                <div class="log-entry ${logClass}" data-log-id="${log.id}">
                    <div class="log-header">
                        <span class="log-icon">${icon}</span>
                        <span class="log-type">${this.formatLogType(log.log_type)}</span>
                        <span class="log-time">${timestamp}</span>
                        ${log.strategy_name ? `<span class="log-strategy">${log.strategy_name}</span>` : ''}
                    </div>
                    <div class="log-message">${log.message}</div>
                    ${log.details ? `<div class="log-details">${this.formatDetails(log.details)}</div>` : ''}
                </div>
            `;
        });
        
        this.logContainer.innerHTML = html;
        
        // Scroll to bottom if new logs
        if (logs.length > 0 && logs[0].id > this.lastLogId) {
            this.logContainer.scrollTop = this.logContainer.scrollHeight;
            this.lastLogId = logs[0].id;
        }
    }
    
    getLogClass(logType) {
        const classes = {
            'DATA_FETCH': 'log-info',
            'INDICATOR_CALC': 'log-info',
            'SIGNAL_GENERATED': 'log-success',
            'TRADE_EXECUTED': 'log-success',
            'TRADE_FAILED': 'log-error',
            'STRATEGY_START': 'log-success',
            'STRATEGY_STOP': 'log-warning',
            'ERROR': 'log-error',
            'INFO': 'log-info'
        };
        return classes[logType] || 'log-info';
    }
    
    getLogIcon(logType) {
        const icons = {
            'DATA_FETCH': '📊',
            'INDICATOR_CALC': '📈',
            'SIGNAL_GENERATED': '🎯',
            'TRADE_EXECUTED': '✅',
            'TRADE_FAILED': '❌',
            'STRATEGY_START': '🚀',
            'STRATEGY_STOP': '⏹️',
            'ERROR': '⚠️',
            'INFO': 'ℹ️'
        };
        return icons[logType] || 'ℹ️';
    }
    
    formatLogType(logType) {
        return logType.replace('_', ' ').toLowerCase();
    }
    
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    }
    
    formatDetails(details) {
        if (typeof details === 'object') {
            let html = '<div class="details-grid">';
            for (const [key, value] of Object.entries(details)) {
                if (key !== 'error') { // Don't show error details in main view
                    html += `<div class="detail-item"><strong>${key}:</strong> ${value}</div>`;
                }
            }
            html += '</div>';
            return html;
        }
        return details;
    }
    
    updateLogCount(count) {
        if (this.logCount) {
            this.logCount.textContent = count;
        }
    }
    
    async clearLogs() {
        if (!confirm('Are you sure you want to clear old logs? This will keep only the last 1000 logs.')) {
            return;
        }
        
        try {
            const response = await fetch('/api/clear-logs/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Old logs cleared successfully', 'success');
                this.loadLogs(); // Reload logs
            } else {
                this.showNotification('Failed to clear logs: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error clearing logs:', error);
            this.showNotification('Error clearing logs', 'error');
        }
    }
    
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">×</button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    }
}

// Initialize bot monitor when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('bot-logs-container')) {
        window.botMonitor = new BotMonitor();
    }
}); 