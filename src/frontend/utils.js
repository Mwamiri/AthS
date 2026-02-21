// ============================================
// AthSys Shared Utilities
// ============================================

// Date Formatting Utilities
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', { 
        month: 'short', day: 'numeric', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

function formatDateLong(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', month: 'long', day: 'numeric' 
    });
}

// Search Debouncing
let searchTimeout;
function debounceSearch(callback, delay = 300) {
    return function(...args) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => callback.apply(this, args), delay);
    };
}

// CSV Export Utility
function exportToCSV(data, filename) {
    if (!data || data.length === 0) {
        alert('No data to export');
        return;
    }
    
    // Get headers from first object
    const headers = Object.keys(data[0]);
    
    // Create CSV content
    const csvContent = [
        headers.join(','), // Header row
        ...data.map(row => 
            headers.map(header => {
                let cell = row[header];
                // Handle commas and quotes in data
                if (typeof cell === 'string') {
                    cell = cell.replace(/"/g, '""'); // Escape quotes
                    if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) {
                        cell = `"${cell}"`;
                    }
                }
                return cell ?? '';
            }).join(',')
        )
    ].join('\n');
    
    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}

// Loading Skeleton Generator
function showLoadingSkeleton(containerId, count = 3, type = 'card') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (type === 'card') {
        container.innerHTML = Array(count).fill(0).map(() => `
            <div class="skeleton-card">
                <div class="skeleton skeleton-title"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text" style="width: 70%;"></div>
                <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                    <div class="skeleton" style="width: 80px; height: 32px;"></div>
                    <div class="skeleton" style="width: 80px; height: 32px;"></div>
                </div>
            </div>
        `).join('');
    } else if (type === 'table') {
        container.innerHTML = `
            <table style="width: 100%;">
                <thead>
                    <tr>
                        ${Array(5).fill('<th><div class="skeleton skeleton-text"></div></th>').join('')}
                    </tr>
                </thead>
                <tbody>
                    ${Array(count).fill(0).map(() => `
                        <tr>
                            ${Array(5).fill('<td><div class="skeleton skeleton-text"></div></td>').join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }
}

// Empty State Generator
function showEmptyState(containerId, config) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const {
        icon = '📭',
        title = 'No items found',
        message = 'Get started by creating your first item',
        actionText = '➕ Create New',
        actionCallback = null,
        showAction = true
    } = config;
    
    container.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">${icon}</div>
            <h3>${title}</h3>
            <p>${message}</p>
            ${showAction && actionCallback ? `
                <button class="btn btn-primary" onclick="${actionCallback}">${actionText}</button>
            ` : ''}
        </div>
    `;
}

// Keyboard Shortcuts Handler
function initKeyboardShortcuts(shortcuts) {
    document.addEventListener('keydown', (e) => {
        // Global shortcuts
        if (e.key === 'Escape') {
            // Close all modals
            document.querySelectorAll('.modal').forEach(modal => {
                modal.style.display = 'none';
            });
        }
        
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Custom shortcuts
        if (shortcuts) {
            shortcuts.forEach(shortcut => {
                if (shortcut.ctrl && !e.ctrlKey) return;
                if (shortcut.shift && !e.shiftKey) return;
                if (shortcut.alt && !e.altKey) return;
                if (e.key.toLowerCase() === shortcut.key.toLowerCase()) {
                    e.preventDefault();
                    shortcut.action();
                }
            });
        }
    });
}

// Table Sorting
function addTableSorting(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const headers = table.querySelectorAll('th[data-sort]');
    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.innerHTML += ' <span class="sort-icon">⇅</span>';
        
        header.addEventListener('click', () => {
            const column = header.dataset.sort;
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            // Toggle sort direction
            const isAsc = header.classList.contains('sort-asc');
            
            // Remove all sort classes
            headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
            
            // Add appropriate class
            header.classList.add(isAsc ? 'sort-desc' : 'sort-asc');
            
            // Sort rows
            rows.sort((a, b) => {
                const aVal = a.querySelector(`td[data-sort="${column}"]`)?.textContent || '';
                const bVal = b.querySelector(`td[data-sort="${column}"]`)?.textContent || '';
                
                if (isAsc) {
                    return bVal.localeCompare(aVal, undefined, { numeric: true });
                } else {
                    return aVal.localeCompare(bVal, undefined, { numeric: true });
                }
            });
            
            // Reorder DOM
            rows.forEach(row => tbody.appendChild(row));
        });
    });
}

// Pagination Helper
function paginate(items, page, itemsPerPage = 20) {
    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return {
        items: items.slice(start, end),
        totalPages: Math.ceil(items.length / itemsPerPage),
        currentPage: page,
        hasNext: end < items.length,
        hasPrev: page > 1
    };
}

function renderPagination(containerId, currentPage, totalPages, onPageChange) {
    const container = document.getElementById(containerId);
    if (!container || totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    const buttons = [];
    
    // Previous button
    buttons.push(`
        <button class="pagination-btn" ${currentPage === 1 ? 'disabled' : ''} 
                onclick="${onPageChange}(${currentPage - 1})">
            ← Previous
        </button>
    `);
    
    // Page numbers (show max 5)
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    
    if (endPage - startPage < 4) {
        startPage = Math.max(1, endPage - 4);
    }
    
    if (startPage > 1) {
        buttons.push(`<button class="pagination-btn" onclick="${onPageChange}(1)">1</button>`);
        if (startPage > 2) buttons.push(`<span class="pagination-ellipsis">...</span>`);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        buttons.push(`
            <button class="pagination-btn ${i === currentPage ? 'active' : ''}" 
                    onclick="${onPageChange}(${i})">
                ${i}
            </button>
        `);
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) buttons.push(`<span class="pagination-ellipsis">...</span>`);
        buttons.push(`<button class="pagination-btn" onclick="${onPageChange}(${totalPages})">${totalPages}</button>`);
    }
    
    // Next button
    buttons.push(`
        <button class="pagination-btn" ${currentPage === totalPages ? 'disabled' : ''} 
                onclick="${onPageChange}(${currentPage + 1})">
            Next →
        </button>
    `);
    
    container.innerHTML = `<div class="pagination">${buttons.join('')}</div>`;
}

// Offline Detection
function initOfflineDetection() {
    window.addEventListener('online', () => {
        if (typeof toast !== 'undefined') {
            toast.show('✅ Back online', 'success');
        }
        // Trigger data reload if there's a global reload function
        if (typeof loadData === 'function') {
            loadData();
        }
    });

    window.addEventListener('offline', () => {
        if (typeof toast !== 'undefined') {
            toast.show('⚠️ You are offline. Some features may not work.', 'warning');
        }
    });
    
    // Check initial state
    if (!navigator.onLine && typeof toast !== 'undefined') {
        toast.show('⚠️ You are offline', 'warning');
    }
}

// Initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initOfflineDetection();
    });
} else {
    initOfflineDetection();
}
