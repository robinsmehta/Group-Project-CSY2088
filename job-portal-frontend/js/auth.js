// js/auth.js — Authentication: Register, Login, Logout
//
// Refactored to use centralized API functions from api.js
// Used by: auth/register.html, auth/login.html
// Depends on: config.js, shared.js, api.js


// registerUser(name, email, password)
// Uses apiRegisterUser from api.js
async function registerUser(name, email, password) {
    const { ok, status, data } = await apiRegisterUser(name, email, password);
    console.log('[Auth API - Register User]:', data);
    return { status, data, ok };
}


// registerCompany(company_name, email, password, description)
// Uses apiRegisterCompany from api.js
async function registerCompany(company_name, email, password, description = '') {
    const { ok, status, data } = await apiRegisterCompany(company_name, email, password, description);
    console.log('[Auth API - Register Company]:', data);
    return { status, data, ok };
}


// loginUser(email, password, role)
// Uses apiLogin from api.js
async function loginUser(email, password, role) {
    const { ok, status, data } = await apiLogin(email, password, role);
    console.log('[Auth API - Login]:', data);
    return { status, data, ok };
}


// logoutUser()
// Uses apiLogout from api.js
async function logoutUser() {
    const { ok, status, data } = await apiLogout();
    console.log('[Auth API - Logout]:', data);
    if (typeof sessionStorage !== 'undefined') sessionStorage.clear();
    return { status, data, ok };
}
