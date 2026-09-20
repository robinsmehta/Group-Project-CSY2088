// js/user-dashboard.js — Candidate Dashboard Logic
// Depends on: config.js, shared.js, api.js

document.addEventListener('DOMContentLoaded', async () => {
    await redirectIfNotLoggedIn('user');
    renderNavbar('dashboard');
    
    const user = getLoggedInUser();
    if (user) {
        document.getElementById('dash-user-name').textContent = user.name || 'User';
    }
    
    await initApplicationsList();
});

async function initApplicationsList() {
    const { ok, data } = await apiGetMyApplications();
    let apps = [];

    if (ok && Array.isArray(data?.applications)) {
        apps = data.applications.map(app => ({
            id:           app.id,
            position:     app.job?.title   || app.job_title   || 'Unknown Position',
            company:      app.job?.company_name || app.company_name || 'Unknown Company',
            applied_date: app.applied_at   || app.created_at  || '',
            status:       app.status        || 'applied',
            resume_url:   app.resume_url || '#',
            job:          app.job
        }));
    }

    const total       = apps.length;
    const inReview    = apps.filter(a => a.status === 'under_review').length;
    const shortlisted = apps.filter(a => a.status === 'shortlisted').length;
    const rejected    = apps.filter(a => a.status === 'rejected').length;

    document.getElementById('stat-total-applied').textContent = total;
    document.getElementById('stat-in-review').textContent = inReview;
    document.getElementById('stat-shortlisted').textContent = shortlisted;
    document.getElementById('stat-rejected').textContent = rejected;

    renderList(apps);
}

let globalAppsList = [];
let activeAppId = null;

function renderList(apps) {
    globalAppsList = apps;
    const container = document.getElementById('applications-list-body');

    if (!apps || apps.length === 0) {
        showEmpty(
            'applications-list-body',
            'No Applications Yet',
            'You haven\'t applied to any jobs yet.',
            '<a href="../jobs/listing.html" class="dashboard-style-096649" style="margin-top: 16px; display: inline-flex;">Browse Jobs →</a>'
        );
        document.getElementById('job-detail-pane').style.display = 'none';
        return;
    }

    container.innerHTML = apps.map(app => {
        const badgeHtml = createStatusBadge(app.status);
        const safeName = escHtml(app.position);
        const safeCompany = escHtml(app.company);
        const appliedDate = app.applied_date ? timeAgo(app.applied_date) : 'Recently';
        const isActive = activeAppId === app.id;
        
        const border = isActive ? 'border: 2px solid #111827;' : 'border: 1px solid #E5E7EB;';
        const padding = isActive ? 'padding: 19px;' : 'padding: 20px;';

        return `
        <div onclick="selectApplication(${app.id})" class="dashboard-app-card" style="${border} ${padding}">
            <div>
                <h4 class="dashboard-style-91f8e7">${safeName}</h4>
                <div class="dashboard-style-49802d">
                    ${safeCompany} &nbsp;•&nbsp; ${escHtml(app.job?.location || 'Remote')}
                </div>
            </div>
            <div class="dashboard-style-7851db">
                <div class="dashboard-style-69a86b">Applied<br>${appliedDate}</div>
                ${badgeHtml}
            </div>
        </div>
        `;
    }).join('');

    // Automatically select the first one if none selected
    if (apps.length > 0 && !activeAppId) {
        selectApplication(apps[0].id);
    }
}

function selectApplication(id) {
    activeAppId = id;
    renderList(globalAppsList);

    const app = globalAppsList.find(a => a.id === id);
    if (!app) return;

    const pane = document.getElementById('job-detail-pane');
    const grid = document.getElementById('main-content-grid');
    pane.style.display = 'block';
    grid.style.gridTemplateColumns = '1fr 1.3fr';

    document.getElementById('detail-title').textContent = app.position;
    document.getElementById('detail-type').textContent = app.job?.job_type || 'Full-time';
    document.getElementById('detail-location').textContent = app.job?.location || 'Remote';
    document.getElementById('detail-salary').textContent = app.job?.salary || 'Competitive';

    let desc = app.job?.description || '<p class="dashboard-style-5534b3">No job description available.</p>';

    if (app.job?.description) {
        let lines = app.job.description.split('\n');
        desc = lines.map(l => l.trim() ? `<p class="dashboard-style-5534b3">${escHtml(l)}</p>` : '').join('');
    }

    document.getElementById('detail-description').innerHTML = desc;

    const resumeBtn = document.getElementById('detail-resume-btn');
    if (app.resume_url && app.resume_url !== '#') {
        resumeBtn.href = app.resume_url;
        resumeBtn.style.opacity = '1';
        resumeBtn.style.pointerEvents = 'auto';
    } else {
        resumeBtn.href = '#';
        resumeBtn.style.opacity = '0.5';
        resumeBtn.style.pointerEvents = 'none';
    }
}

function escHtml(str) {
    const d = document.createElement('div');
    d.textContent = str || '';
    return d.innerHTML;
}
