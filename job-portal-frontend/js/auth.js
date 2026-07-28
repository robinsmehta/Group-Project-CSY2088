// ============================================================
// js/auth.js — Authentication: Register, Login, Logout
//
// Handles basic fetch() calls related to user authentication.
// Used by: auth/register.html, auth/login.html
// Depends on: config.js (for API_BASE_URL), shared.js
// ============================================================


// ------------------------------------------------------------
// registerUser(event)
// Sends basic POST request to /api/auth/register/user endpoint.
// ------------------------------------------------------------
async function registerUser(event) {
    if (event) event.preventDefault();
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register/user`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: 'Test User', email: 'test@example.com', password: 'password123' })
        });
        const data = await response.json();
        console.log('[Auth Route Connection - Register User]:', data);
        showMessage('register-message', data.message || 'Connected to backend endpoint!', 'info');
        return data;
    } catch (error) {
        console.error('[Auth Route Error - Register User]:', error);
        showMessage('register-message', 'Backend connection error. Make sure server is running.', 'error');
    }
}


// ------------------------------------------------------------
// registerCompany(event)
// Sends basic POST request to /api/auth/register/company endpoint.
// ------------------------------------------------------------
async function registerCompany(event) {
    if (event) event.preventDefault();
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register/company`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company_name: 'Test Company', email: 'company@example.com', password: 'password123', description: 'Test' })
        });
        const data = await response.json();
        console.log('[Auth Route Connection - Register Company]:', data);
        showMessage('register-message', data.message || 'Connected to backend endpoint!', 'info');
        return data;
    } catch (error) {
        console.error('[Auth Route Error - Register Company]:', error);
        showMessage('register-message', 'Backend connection error.', 'error');
    }
}


// ------------------------------------------------------------
// loginUser(event)
// Sends basic POST request to /api/auth/login endpoint.
// ------------------------------------------------------------
async function loginUser(event) {
    if (event) event.preventDefault();
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: 'test@example.com', password: 'password123', role: 'user' })
        });
        const data = await response.json();
        console.log('[Auth Route Connection - Login]:', data);
        showMessage('login-message', data.message || 'Connected to backend endpoint!', 'info');
        return data;
    } catch (error) {
        console.error('[Auth Route Error - Login]:', error);
        showMessage('login-message', 'Backend connection error.', 'error');
    }
}


// ------------------------------------------------------------
// logoutUser()
// Sends basic POST request to /api/auth/logout endpoint.
// ------------------------------------------------------------
async function logoutUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/logout`, { method: 'POST' });
        const data = await response.json();
        console.log('[Auth Route Connection - Logout]:', data);
        sessionStorage.clear();
        return data;
    } catch (error) {
        console.error('[Auth Route Error - Logout]:', error);
    }
}


// ------------------------------------------------------------
// showTab(role)
// UI helper for tab switching.
// ------------------------------------------------------------
function showTab(role) {
    console.log('[UI Switch Tab]:', role);
}


// ------------------------------------------------------------
// setLoginRole(role)
// UI helper for login role selection.
// ------------------------------------------------------------
function setLoginRole(role) {
    console.log('[UI Set Login Role]:', role);
}

