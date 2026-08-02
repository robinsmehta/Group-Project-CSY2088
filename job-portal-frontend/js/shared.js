// js/shared.js — Shared Utilities, Navbar, Footer, Toasts
// Depends on: config.js
// Load on every page after config.js

// Navbar & Footer Injection

function renderNavbar(activePage) {
    const user = getLoggedInUser();

    let links = [];
    if (!user) {
        links = [
            { href: '/index.html',        label: 'Home',      key: 'home' },
            { href: '/jobs/listing.html', label: 'Find Jobs', key: 'jobs' }
        ];
    } else if (user.role === 'company') {
        links = [
            { href: '/company/dashboard.html',             label: 'Dashboard',       key: 'dashboard' },
            { href: '/company/dashboard.html#manage-jobs',  label: 'Manage Jobs',     key: 'manage-jobs' },
            { href: '/company/applicants.html',            label: 'Applicants',      key: 'applicants' },
            { href: '/company/dashboard.html#profile',      label: 'Company Profile', key: 'profile' }
        ];
    } else {
        links = [
            { href: '/user/dashboard.html',             label: 'Dashboard',       key: 'dashboard' },
            { href: '/jobs/listing.html',               label: 'Jobs',            key: 'jobs' },
            { href: '/user/dashboard.html#applications',label: 'My Applications', key: 'applications' },
            { href: '/user/dashboard.html#profile',     label: 'Profile',         key: 'profile' }
        ];
    }

    const navLinks = links.map(l => {
        const isActive = activePage === l.key ? ' active' : '';
        return `<a href="${l.href}" class="${isActive}">${l.label}</a>`;
    }).join('');

    let authSection = '';
    if (user) {
        const name = user.name || user.company_name || 'User';
        const initials = name.charAt(0).toUpperCase();
        const dashHref = user.role === 'company'
            ? '/company/dashboard.html'
            : user.role === 'admin'
                ? '/admin/dashboard.html'
                : '/user/dashboard.html';

        authSection = `
            <a href="${dashHref}" class="navbar-user">
                <span class="navbar-user-avatar">${initials}</span>
                <span>${name}</span>
            </a>
            <button class="btn btn-ghost btn-sm" id="btn-logout">Logout</button>
        `;
    } else {
        authSection = `
            <a href="/auth/login.html" class="btn btn-ghost btn-sm">Sign in</a>
            <a href="/auth/register.html" class="btn btn-primary btn-sm">Register</a>
        `;
    }

    const mobileLinks = links.map(l =>
        `<a href="${l.href}">${l.label}</a>`
    ).join('');

    const html = `
        <nav class="navbar" id="navbar">
            <div class="navbar-inner">
                <a href="/index.html" class="navbar-brand">HireHub</a>
                <div class="navbar-links">${navLinks}</div>
                <div class="navbar-actions">${authSection}</div>
                <button class="navbar-hamburger" id="nav-hamburger" aria-label="Menu">
                    <span></span><span></span><span></span>
                </button>
            </div>
            <div class="navbar-mobile" id="nav-mobile">
                ${mobileLinks}
                <div class="mobile-actions">
                    ${user
                        ? `<button class="btn btn-ghost btn-sm" id="btn-logout-mobile">Logout</button>`
                        : `<a href="/auth/login.html" class="btn btn-outline btn-sm">Sign in</a>
                           <a href="/auth/register.html" class="btn btn-primary btn-sm">Register</a>`
                    }
                </div>
            </div>
        </nav>
    `;

    const el = document.getElementById('navbar') || document.querySelector('.navbar');
    if (el) el.outerHTML = html;

    const hamburger = document.getElementById('nav-hamburger');
    const mobileMenu = document.getElementById('nav-mobile');
    if (hamburger && mobileMenu) {
        hamburger.addEventListener('click', () => mobileMenu.classList.toggle('open'));
    }

    document.getElementById('btn-logout')?.addEventListener('click', handleLogout);
    document.getElementById('btn-logout-mobile')?.addEventListener('click', handleLogout);
}

function renderFooter() {
    const html = `
        <footer class="footer" id="footer">
            <div class="footer-inner">
                <div>
                    <div class="footer-brand-name">HireHub</div>
                    <p class="footer-tagline">Connecting talent with opportunity. Find your next role or your next great hire.</p>
                </div>
                <div class="footer-col">
                    <h4>For Job Seekers</h4>
                    <ul>
                        <li><a href="/jobs/listing.html">Browse Jobs</a></li>
                        <li><a href="/auth/register.html">Create Account</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>For Employers</h4>
                    <ul>
                        <li><a href="/auth/register.html">Post a Job</a></li>
                        <li><a href="/company/dashboard.html">Employer Dashboard</a></li>
                        <li><a href="/company/applicants.html">View Applicants</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Company</h4>
                    <ul>
                        <li><a href="#">About Us</a></li>
                        <li><a href="#">Contact</a></li>
                        <li><a href="#">Privacy Policy</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom page-container">
                <span>&copy; ${new Date().getFullYear()} HireHub. All rights reserved.</span>
            </div>
        </footer>
    `;

    const el = document.getElementById('footer') || document.querySelector('.footer');
    if (el) el.outerHTML = html;
}

// Auth Helpers

function getLoggedInUser() {
    const raw = sessionStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
}

function setLoggedInUser(data) {
    sessionStorage.setItem('user', JSON.stringify(data));
}

function redirectIfNotLoggedIn(requiredRole) {
    const user = getLoggedInUser();
    if (!user) {
        window.location.href = '/auth/login.html';
        return;
    }
    if (requiredRole && user.role !== requiredRole) {
        if (user.role === 'company') {
            window.location.href = '/company/dashboard.html';
        } else if (user.role === 'user' || user.role === 'candidate') {
            window.location.href = '/user/dashboard.html';
        } else {
            window.location.href = '/index.html';
        }
    }
}

async function handleLogout() {
    try {
        await fetch(`${API_BASE_URL}/auth/logout`, { method: 'POST', credentials: 'include' });
    } catch (_) {}
    sessionStorage.clear();
    window.location.href = '/index.html';
}

// Toast Notifications

function initToastContainer() {
    if (document.getElementById('toast-container')) return;
    const div = document.createElement('div');
    div.id = 'toast-container';
    div.className = 'toast-container';
    document.body.appendChild(div);
}

function showToast(message, type = 'info', duration = 3500) {
    initToastContainer();
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = {
        success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
        error:   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
        warning: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        info:    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    };

    toast.innerHTML = `${icons[type] || icons.info} <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        toast.style.transition = '0.2s ease';
        setTimeout(() => toast.remove(), 220);
    }, duration);
}

// Message Helper

function showMessage(elementId, message, type = 'info') {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = message;
    el.className = `form-message ${type}`;
    el.style.display = 'block';
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideMessage(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.style.display = 'none';
}

// Date Formatting

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-GB', {
        day: 'numeric', month: 'short', year: 'numeric'
    });
}

function timeAgo(dateString) {
    if (!dateString) return '';
    const diff = Math.floor((Date.now() - new Date(dateString)) / 1000);
    if (diff < 60)        return 'Just now';
    if (diff < 3600)      return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400)     return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 604800)    return `${Math.floor(diff / 86400)}d ago`;
    return formatDate(dateString);
}

// Badge Helper

function createStatusBadge(status) {
    const safe = (status || 'unknown').toLowerCase().replace(/\s+/g, '_');
    const label = safe.replace(/_/g, ' ');
    return `<span class="badge badge-${safe}">${label}</span>`;
}

// Loader Helpers

function showLoader(containerId, message = 'Loading…') {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = `<div class="loader"><div class="spinner"></div>${message}</div>`;
}

function showEmpty(containerId, title = 'Nothing here yet', message = '', actionHtml = '') {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = `
        <div class="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <h3>${title}</h3>
            ${message ? `<p>${message}</p>` : ''}
            ${actionHtml}
        </div>
    `;
}

// API Health Check

async function checkApiHealth() {
    try {
        const res = await fetch(`${API_BASE_URL}/health`);
        const data = await res.json();
        console.log('[API] Connected:', data.message);
        return true;
    } catch {
        console.warn('[API] Cannot reach backend at', API_BASE_URL);
        return false;
    }
}

document.addEventListener('DOMContentLoaded', checkApiHealth);
