// js/shared.js — Shared Utilities, Navbar, Footer, Toasts
// Depends on: config.js
// Load on every page after config.js

// ============================================================
// TODO — TASK-001 — Naming update: "HireHub" → "Job Portal"
// ============================================================
// PROBLEM: The site is now called "Job Portal", not "HireHub" (the old
// name). This file builds the navbar brand text and the footer brand text
// further down — search this file for the literal text "HireHub" (there
// are 2 places: the navbar logo/brand link, and the footer heading) and
// replace both with "Job Portal". The same text also appears in the
// <title> tag and other spots across every HTML page — as you (Robins)
// rebuild each page from Figma, make sure "HireHub" doesn't survive
// anywhere (page titles, footer, navbar).
// ASSIGNED TASK: Robins (A1) — Naming update, part of rebuilding every page.
// ============================================================

// ============================================================
// TODO — TASK-002 — Build the shared Profile Edit popover's BEHAVIOUR
// ============================================================
//
// PROBLEM:
// Robins (A2) is building what the Profile Edit popover LOOKS like — a
// small floating box with Name, Email, Password fields (+ Description for
// companies) that opens when the circle icon in the navbar is clicked.
// Right now nothing in this file makes that popover actually open, close,
// load the current user's info, or save changes. Since the same circle
// icon appears on almost every page, this needs to be built ONCE here in
// shared.js, not separately on each page.
//
// WHAT YOU NEED TO DO:
// 1. Once Robins has a rough version of the popover HTML/CSS, add a
//    function here, e.g. `initProfilePopover()`, that:
//      a) Finds the circle icon in the navbar (rendered inside
//         `renderNavbar()` below — look for the `navbar-user-avatar` /
//         `navbar-user` markup a little further down in this function)
//         and adds a click listener that shows/hides the popover.
//      b) When opened, fills the Name/Email fields with the currently
//         logged-in user's info — you already have this in
//         `getLoggedInUser()` further down this file.
//      c) When the "Update" button inside the popover is clicked, sends
//         the new name/email/password to the backend using the new
//         `apiUpdateMyProfile(role, payload)` helper (see the TODO for
//         this in js/api.js — TASK-010) and shows a success/error message
//         (reuse `showToast()` from this same file).
//      d) Closes when clicking outside the popover or on an "X" button.
// 2. Call `initProfilePopover()` from inside `renderNavbar()` below, after
//    the navbar HTML has been inserted into the page (so the circle icon
//    actually exists in the DOM by the time you try to attach the click
//    listener to it).
//
// HOW THIS PART CONNECTS:
// renderNavbar() below (which runs on every page) builds the circle icon
// markup. Your popover logic attaches to that same icon. The popover then
// talks to the backend routes Ugeesha/Simrika/Reeju are each adding
// (TASK-009 in app/routes/auth_routes.py) via the new apiUpdateMyProfile
// helper (TASK-010 in js/api.js).
//
// WHAT "DONE" LOOKS LIKE:
// On any page, clicking the circle icon lets you actually update your
// name/email/password, and it behaves the same way no matter which page
// you're on.
//
// ASSIGNED TASK:
// Sagar (B1) — Build the Profile Edit popover's actual behavior.
// ============================================================

// Navbar & Footer Injection

function renderNavbar(activePage) {
    const user = getLoggedInUser();

    let links = [];
    if (!user) {
        links = [
            { href: resolveSitePath('index.html'),        label: 'Home',      key: 'home' },
            { href: resolveSitePath('jobs/listing.html'), label: 'Find Jobs', key: 'jobs' }
        ];
    } else if (user.role === 'company') {
        const dashboardHref = resolveSitePath('company/dashboard.html');
        links = [
            { href: dashboardHref, label: 'Dashboard',       key: 'dashboard' },
            { href: resolveSitePath('company/applicants.html'), label: 'Applicants',      key: 'applicants' },
            { href: resolveSitePath('company/post-job.html'), label: 'Post Job',        key: 'post-job' }
        ];
    } else if (user.role === 'admin') {
        links = [
            { href: resolveSitePath('admin/dashboard.html'), label: 'Dashboard', key: 'dashboard' }
        ];
    } else {
        links = [
            { href: resolveSitePath('user/dashboard.html'), label: 'Dashboard',       key: 'dashboard' },
            { href: resolveSitePath('jobs/listing.html'), label: 'Browse Jobs',     key: 'jobs' },
            { href: resolveSitePath('user/dashboard.html'), label: 'My Applications', key: 'applications' }
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
            ? resolveSitePath('company/dashboard.html')
            : user.role === 'admin'
                ? resolveSitePath('admin/dashboard.html')
                : resolveSitePath('user/dashboard.html');

        // NOTE for Robins (A2): the logged-in person's name label next to
        // the profile circle (the "New small addition" in the brief) is
        // already implemented right here — `${name}` is rendered next to
        // the avatar circle below. When you rebuild the navbar to match
        // Figma, just make sure this name label survives in your new markup.
        authSection = `
            <a href="${dashHref}" class="navbar-user">
                <span class="navbar-user-avatar">${initials}</span>
                <span>${name}</span>
            </a>
            <button class="btn btn-ghost btn-sm" id="btn-logout">Logout</button>
        `;
    } else {
        authSection = `
            <a href="${resolveSitePath('auth/login.html')}" class="btn btn-ghost btn-sm">Sign in</a>
            <a href="${resolveSitePath('auth/register.html')}" class="btn btn-primary btn-sm">Register</a>
        `;
    }

    const mobileLinks = links.map(l =>
        `<a href="${l.href}">${l.label}</a>`
    ).join('');

    const html = `
        <nav class="navbar" id="navbar">
            <div class="navbar-inner">
                <!-- TODO — TASK-001 (Robins/A1): rename "HireHub" to "Job Portal" below -->
                <a href="${resolveSitePath('index.html')}" class="navbar-brand">HireHub</a>
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
                        : `<a href="${resolveSitePath('auth/login.html')}" class="btn btn-outline btn-sm">Sign in</a>
                           <a href="${resolveSitePath('auth/register.html')}" class="btn btn-primary btn-sm">Register</a>`
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
                    <!-- TODO — TASK-001 (Robins/A1): rename "HireHub" to "Job Portal" below (2 spots in this footer block) -->
                    <div class="footer-brand-name">HireHub</div>
                    <p class="footer-tagline">Connecting talent with opportunity. Find your next role or your next great hire.</p>
                </div>
                <div class="footer-col">
                    <h4>For Job Seekers</h4>
                    <ul>
                        <li><a href="${resolveSitePath('jobs/listing.html')}">Browse Jobs</a></li>
                        <li><a href="${resolveSitePath('auth/register.html')}">Create Account</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>For Employers</h4>
                    <ul>
                        <li><a href="${resolveSitePath('auth/register.html')}">Post a Job</a></li>
                        <li><a href="${resolveSitePath('company/dashboard.html')}">Employer Dashboard</a></li>
                        <li><a href="${resolveSitePath('company/applicants.html')}">View Applicants</a></li>
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

// Path Helpers

function resolveSitePath(route) {
    if (typeof window === 'undefined' || !window.location || !route) return route || '';

    const normalizedRoute = String(route).trim();
    if (!normalizedRoute || normalizedRoute.startsWith('#') || normalizedRoute.startsWith('?') || /^[a-z]+:\/\//i.test(normalizedRoute)) {
        return normalizedRoute;
    }

    const currentPath = window.location.pathname.replace(/\\/g, '/');
    const segments = currentPath.split('/').filter(Boolean);
    const rootIndex = segments.lastIndexOf('job-portal-frontend');
    const siteSegments = rootIndex >= 0 ? segments.slice(rootIndex + 1) : segments;
    const currentDirSegments = siteSegments.length > 1 ? siteSegments.slice(0, -1) : [];
    const targetSegments = normalizedRoute.replace(/^\/+/, '').split('/').filter(Boolean);

    let commonLength = 0;
    while (commonLength < currentDirSegments.length && commonLength < targetSegments.length && currentDirSegments[commonLength] === targetSegments[commonLength]) {
        commonLength += 1;
    }

    const relParts = [
        ...Array.from({ length: currentDirSegments.length - commonLength }, () => '..'),
        ...targetSegments.slice(commonLength)
    ];

    const relativePath = relParts.join('/').replace(/\/{2,}/g, '/');
    return relativePath || './';
}

// Auth Helpers

function clearAuthState() {
    if (typeof sessionStorage !== 'undefined') {
        sessionStorage.removeItem('user');
        sessionStorage.removeItem('user_kanban_applications');
    }
}

function getLoggedInUser() {
    const raw = sessionStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
}

function setLoggedInUser(data) {
    if (!data) {
        clearAuthState();
        return;
    }
    sessionStorage.setItem('user', JSON.stringify(data));
}

async function redirectIfNotLoggedIn(requiredRole) {
    try {
        const res = await fetch(`${API_BASE_URL}/auth/me`, { credentials: 'include' });
        const data = await res.json().catch(() => ({}));

        if (!res.ok || !data.user) {
            clearAuthState();
            window.location.href = resolveSitePath('auth/login.html');
            return false;
        }

        setLoggedInUser(data.user);

        if (requiredRole && data.user.role !== requiredRole) {
            if (data.user.role === 'company') {
                window.location.href = resolveSitePath('company/dashboard.html');
            } else if (data.user.role === 'user') {
                window.location.href = resolveSitePath('user/dashboard.html');
            } else if (data.user.role === 'admin') {
                window.location.href = resolveSitePath('admin/dashboard.html');
            } else {
                window.location.href = resolveSitePath('index.html');
            }
            return false;
        }

        return true;
    } catch (_) {
        clearAuthState();
        window.location.href = resolveSitePath('auth/login.html');
        return false;
    }
}

async function handleLogout() {
    try {
        await fetch(`${API_BASE_URL}/auth/logout`, { method: 'POST', credentials: 'include' });
    } catch (_) {}
    clearAuthState();
    window.location.href = resolveSitePath('index.html');
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
        const res = await fetch(`${API_BASE_URL}/health`, { credentials: 'include' });
        const data = await res.json();
        console.log('[API] Connected:', data.message);
        return true;
    } catch {
        console.warn('[API] Cannot reach backend at', API_BASE_URL);
        return false;
    }
}

document.addEventListener('DOMContentLoaded', checkApiHealth);
