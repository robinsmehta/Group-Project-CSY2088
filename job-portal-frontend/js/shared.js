// ============================================================
// js/shared.js — Shared Helper Functions
//
// Contains utility functions used across multiple pages.
// Load this file on every page AFTER config.js.
// ============================================================


// ------------------------------------------------------------
// showMessage(elementId, message, type)
// Displays a success, error, or info message inside a given element.
// type: 'success' | 'error' | 'info'
// ------------------------------------------------------------
function showMessage(elementId, message, type = 'info') {
    const el = document.getElementById(elementId);
    if (!el) return;

    el.textContent = message;
    el.className = `form-message ${type}`;
    el.style.display = 'block';
}


// ------------------------------------------------------------
// formatDate(dateString)
// Converts a raw ISO date string into a readable format like "28 Jul 2024".
// ------------------------------------------------------------
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });
}


// ------------------------------------------------------------
// getLoggedInUser()
// Returns the currently logged-in user's data from sessionStorage.
// Returns null if no user is logged in.
// ------------------------------------------------------------
function getLoggedInUser() {
    const userJson = sessionStorage.getItem('user');
    return userJson ? JSON.parse(userJson) : null;
}


// ------------------------------------------------------------
// redirectIfNotLoggedIn(requiredRole)
// Checks if the user is logged in and has the right role.
// If not, redirects to login.html.
// ------------------------------------------------------------
function redirectIfNotLoggedIn(requiredRole) {
    const user = getLoggedInUser();
    if (!user || (requiredRole && user.role !== requiredRole)) {
        window.location.href = '/auth/login.html';
    }
}


// ------------------------------------------------------------
// createStatusBadge(status)
// Returns an HTML string for a styled status badge pill.
// ------------------------------------------------------------
function createStatusBadge(status) {
    const safeStatus = (status || 'unknown').toLowerCase();
    const formatted = safeStatus.replace('_', ' ').toUpperCase();
    return `<span class="badge badge-${safeStatus}">${formatted}</span>`;
}


// ------------------------------------------------------------
// checkApiHealth()
// Connection test function: sends a request to the backend health check.
// Logs connection status to the browser console.
// ------------------------------------------------------------
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('[API Connection Success]:', data.message);
        return true;
    } catch (error) {
        console.warn('[API Connection Failed]: Cannot reach backend at', `${API_BASE_URL}/health`);
        return false;
    }
}

// Run health check on page load to verify frontend-backend connection
document.addEventListener('DOMContentLoaded', checkApiHealth);

