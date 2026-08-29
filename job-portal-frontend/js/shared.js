// js/shared.js — Shared Utilities, Navbar, Footer, Toasts
// Depends on: config.js
// Load on every page after config.js

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
            { href: resolveSitePath('admin/dashboard.html'),          label: 'Overview',           key: 'dashboard' },
            { href: resolveSitePath('admin/company-approvals.html'),   label: 'Company Approvals',  key: 'approvals' },
            { href: resolveSitePath('admin/user-directory.html'),      label: 'User Directory',     key: 'users' }
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

        const addAdminBtn = user.role === 'admin' ? '<button class="btn btn-outline btn-sm" id="navbar-add-admin" style="margin-right: 12px; background: #111827; color: white; border-radius: 20px; padding: 6px 14px; font-weight: 600;">Add admin</button>' : '';

        // NOTE for Robins (A2): the logged-in person's name label next to
        // the profile circle (the "New small addition" in the brief) is
        // already implemented right here — `${name}` is rendered next to
        // the avatar circle below. When you rebuild the navbar to match
        // Figma, just make sure this name label survives in your new markup.
        const logoutBtn = `<button class="btn btn-ghost btn-sm" id="btn-logout" style="margin-left: 12px; background:#DC2626; color:white; border-radius:20px; padding:6px 14px; font-weight:600; border:none; cursor:pointer;">Log Out</button>`;

        authSection = `
            ${addAdminBtn}
            <div style="display: flex; align-items: center; gap: 8px;">
                <button id="profile-modal-trigger" style="background:none; border:none; cursor:pointer; font-weight:700; font-size:14px; color:#111827; font-family:inherit;">
                    ${name}
                </button>
                ${logoutBtn}
            </div>

            <!-- Profile Edit Modal -->
            <div id="profile-modal" style="display: none; position: fixed; inset: 0; background: rgba(17, 24, 39, 0.6); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(4px);">
                <div style="background: #ffffff; border-radius: 24px; padding: 40px; width: 100%; max-width: 440px; box-shadow: 0 20px 60px rgba(0,0,0,0.1); position: relative; text-align: left;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px;">
                        <h4 style="margin:0; font-size: 24px; font-weight: 700; color: #111827; letter-spacing: -0.5px;">Profile Edit</h4>
                        <button id="profile-modal-close" style="background:none; border:none; font-size: 20px; cursor: pointer; color: #111827; line-height: 1;">✕</button>
                    </div>
                    
                    <div id="profile-error" class="auth-error-box" style="display:none; margin-bottom: 20px;"></div>
                    
                    <div class="form-group" style="margin-bottom: 16px;">
                        <label style="display:block; font-size: 12px; font-weight: 700; margin-bottom: 8px; color: #374151;">Name</label>
                        <input type="text" id="popover-name" value="${name}" style="width: 100%; padding: 12px 16px; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 12px; font-size: 14px; color: #111827; box-sizing: border-box;">
                    </div>
                    <div class="form-group" style="margin-bottom: 16px;">
                        <label style="display:block; font-size: 12px; font-weight: 700; margin-bottom: 8px; color: #374151;">Email Address</label>
                        <input type="email" id="popover-email" value="${user.email}" style="width: 100%; padding: 12px 16px; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 12px; font-size: 14px; color: #111827; box-sizing: border-box;">
                    </div>
                    ${user.role === 'company' ? `
                    <div class="form-group" style="margin-bottom: 16px;">
                        <label style="display:block; font-size: 12px; font-weight: 700; margin-bottom: 8px; color: #374151;">Description</label>
                        <textarea id="popover-description" rows="3" style="width: 100%; padding: 12px 16px; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 12px; font-size: 14px; color: #111827; box-sizing: border-box;">${user.description || ''}</textarea>
                    </div>
                    ` : ''}
                    <div class="form-group" style="margin-bottom: 32px;">
                        <label style="display:block; font-size: 12px; font-weight: 700; margin-bottom: 8px; color: #374151;">Password (leave blank to keep current)</label>
                        <input type="password" id="popover-password" placeholder="••••••••••••" style="width: 100%; padding: 12px 16px; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 12px; font-size: 14px; color: #111827; box-sizing: border-box;">
                    </div>
                    <button id="popover-update-btn" style="width: 100%; background: #111827; color: #ffffff; padding: 16px; border: none; border-radius: 30px; font-size: 15px; font-weight: 700; cursor: pointer; transition: transform 0.1s;">Update</button>
                </div>
            </div>

            <!-- Add Admin Modal -->
            <div id="add-admin-modal" style="display: none; position: fixed; inset: 0; background: rgba(17, 24, 39, 0.6); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(4px);">
                <div style="background: #ffffff; border-radius: 24px; padding: 40px; width: 100%; max-width: 440px; box-shadow: 0 20px 60px rgba(0,0,0,0.1); position: relative; text-align: left;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px;">
                        <h4 style="margin:0; font-size: 24px; font-weight: 700; color: #111827; letter-spacing: -0.5px;">Add Admin</h4>
                        <button id="add-admin-modal-close" style="background:none; border:none; font-size: 20px; cursor: pointer; color: #111827; line-height: 1;">✕</button>
                    </div>
                    
                    <div class="form-group" style="margin-bottom: 16px;">
                        <label style="display:block; font-size: 12px; font-weight: 700; margin-bottom: 8px; color: #374151;">Name</label>
                        <input type="text" id="admin-name" placeholder="e.g. Jane Doe" style="width: 100%; padding: 12px 16px; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 12px; font-size: 14px; color: #111827; box-sizing: border-box;">
                    </div>
                    <div class="form-group" style="margin-bottom: 16px;">
                        <label style="display:block; font-size: 12px; font-weight: 700; margin-bottom: 8px; color: #374151;">Email Address</label>
                        <input type="email" id="admin-email" placeholder="jane.doe@example.com" style="width: 100%; padding: 12px 16px; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 12px; font-size: 14px; color: #111827; box-sizing: border-box;">
                    </div>
                    <div class="form-group" style="margin-bottom: 32px;">
                        <label style="display:block; font-size: 12px; font-weight: 700; margin-bottom: 8px; color: #374151;">Password</label>
                        <input type="password" id="admin-password" placeholder="••••••••••••" style="width: 100%; padding: 12px 16px; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 12px; font-size: 14px; color: #111827; box-sizing: border-box;">
                    </div>
                    <button id="add-admin-btn" style="width: 100%; background: #000000; color: #ffffff; padding: 16px; border: none; border-radius: 30px; font-size: 15px; font-weight: 700; cursor: pointer;">Add</button>
                </div>
            </div>
        `;
    } else {
        authSection = `
            <div style="display: flex; align-items: center; gap: 24px;">
                <a href="${resolveSitePath('auth/login.html')}" style="color: #111827; font-weight: 600; font-size: 14px; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>
                    Login
                </a>
                <a href="${resolveSitePath('auth/register.html')}" style="background: #111827; color: #ffffff; padding: 10px 24px; border-radius: 24px; font-weight: 600; font-size: 14px; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                    Register
                </a>
            </div>
        `;
    }

    const mobileLinks = links.map(l =>
        `<a href="${l.href}">${l.label}</a>`
    ).join('');

    const html = `
        <nav class="navbar" id="navbar">
            <div class="navbar-inner">
                <!-- TODO — TASK-001 (Robins/A1): rename "Job Portal" to "Job Portal" below -->
                <a href="${resolveSitePath('index.html')}" class="navbar-brand">Job Portal</a>
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

    // Modal Trigger Logic
    const modalTrigger = document.getElementById('profile-modal-trigger');
    const modal = document.getElementById('profile-modal');
    const modalClose = document.getElementById('profile-modal-close');
    
    if (modalTrigger && modal && modalClose) {
        modalTrigger.addEventListener('click', () => modal.style.display = 'flex');
        modalClose.addEventListener('click', () => modal.style.display = 'none');
        modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });
    }

    // Add Admin Modal Trigger Logic
    const addAdminTrigger = document.getElementById('navbar-add-admin');
    const addAdminModal = document.getElementById('add-admin-modal');
    const addAdminClose = document.getElementById('add-admin-modal-close');
    
    if (addAdminTrigger && addAdminModal && addAdminClose) {
        addAdminTrigger.addEventListener('click', () => addAdminModal.style.display = 'flex');
        addAdminClose.addEventListener('click', () => addAdminModal.style.display = 'none');
        addAdminModal.addEventListener('click', (e) => { if (e.target === addAdminModal) addAdminModal.style.display = 'none'; });
    }

    const addAdminBtnSubmit = document.getElementById('add-admin-btn');
    if (addAdminBtnSubmit) {
        addAdminBtnSubmit.addEventListener('click', async () => {
            const name     = document.getElementById('admin-name').value.trim();
            const email    = document.getElementById('admin-email').value.trim();
            const password = document.getElementById('admin-password').value;
            if (!name || !email || !password) {
                if (typeof showToast === 'function') showToast('Please fill in all fields.', 'error');
                else alert('Please fill in all fields.');
                return;
            }
            addAdminBtnSubmit.disabled = true;
            addAdminBtnSubmit.textContent = 'Adding...';
            
            // Assume apiCreateAdmin is available globally from api.js
            if (typeof apiCreateAdmin === 'function') {
                const { ok, data } = await apiCreateAdmin(name, email, password);
                addAdminBtnSubmit.disabled = false;
                addAdminBtnSubmit.textContent = 'Add';

                if (ok) {
                    if (typeof showToast === 'function') showToast('Admin created successfully', 'success');
                    else alert('Admin created successfully');
                    addAdminModal.style.display = 'none';
                    document.getElementById('admin-name').value = '';
                    document.getElementById('admin-email').value = '';
                    document.getElementById('admin-password').value = '';
                } else {
                    if (typeof showToast === 'function') showToast(data.error || 'Failed to create admin', 'error');
                    else alert(data.error || 'Failed to create admin');
                }
            } else {
                addAdminBtnSubmit.disabled = false;
                addAdminBtnSubmit.textContent = 'Add';
                alert('API not loaded');
            }
        });
    }

    document.getElementById('btn-logout')?.addEventListener('click', handleLogout);
    document.getElementById('btn-logout-mobile')?.addEventListener('click', handleLogout);
}

function renderFooter() {
    const html = `
        <footer class="footer" id="footer" style="background-color: #ffffff; border-top: 1px solid #E5E7EB; padding: 24px 20px;">
            <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;">
                <div style="color: #111827; font-size: 16px; font-weight: 800; letter-spacing: -0.5px;">Job Portal</div>
                <div style="font-size: 12px; color: #9CA3AF;">© All rights reserved 2026</div>
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
