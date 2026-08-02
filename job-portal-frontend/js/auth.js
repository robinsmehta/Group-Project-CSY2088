// js/auth.js — Authentication: Register, Login, Logout
//
// Handles fetch() API calls related to user authentication.
// Used by: auth/register.html, auth/login.html
// Depends on: config.js (for API_BASE_URL), shared.js


// registerUser(name, email, password)
// Sends POST request to /api/auth/register/user endpoint.
async function registerUser(name, email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register/user`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include', // Includes session cookie for authentication
            body: JSON.stringify({ name, email, password })
        });
        const data = await response.json();
        console.log('[Auth API - Register User]:', data);
        return { status: response.status, data };
    } catch (error) {
        console.error('[Auth API Error - Register User]:', error);
        return { status: 500, data: { error: 'Network or server error.' } };
    }
}


// registerCompany(company_name, email, password, description)
// Sends POST request to /api/auth/register/company endpoint.
async function registerCompany(company_name, email, password, description = '') {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register/company`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ company_name, email, password, description })
        });
        const data = await response.json();
        console.log('[Auth API - Register Company]:', data);
        return { status: response.status, data };
    } catch (error) {
        console.error('[Auth API Error - Register Company]:', error);
        return { status: 500, data: { error: 'Network or server error.' } };
    }
}


// loginUser(email, password, role)
// Sends POST request to /api/auth/login endpoint.
async function loginUser(email, password, role) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include', // Saves session cookie in browser
            body: JSON.stringify({ email, password, role })
        });
        const data = await response.json();
        console.log('[Auth API - Login]:', data);
        return { status: response.status, data };
    } catch (error) {
        console.error('[Auth API Error - Login]:', error);
        return { status: 500, data: { error: 'Network or server error.' } };
    }
}


// logoutUser()
// Sends POST request to /api/auth/logout endpoint.
async function logoutUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await response.json();
        console.log('[Auth API - Logout]:', data);
        if (typeof sessionStorage !== 'undefined') sessionStorage.clear();
        return { status: response.status, data };
    } catch (error) {
        console.error('[Auth API Error - Logout]:', error);
        return { status: 500, data: { error: 'Network or server error.' } };
    }
}
