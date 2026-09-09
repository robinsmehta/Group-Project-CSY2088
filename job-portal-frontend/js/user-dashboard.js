const fallbackApps = [
            { id: 1, position: 'Senior Product Designer', company: 'TechPulse Labs', applied_date: '2026-07-28', status: 'applied', resume_url: '#' },
            { id: 2, position: 'Frontend Engineer', company: 'BrightWave Tech', applied_date: '2026-07-25', status: 'under_review', resume_url: '#' },
            { id: 3, position: 'Full Stack Developer', company: 'InnoTech Solutions', applied_date: '2026-07-20', status: 'shortlisted', resume_url: '#' },
            { id: 4, position: 'Financial Analyst', company: 'Prime Bank', applied_date: '2026-07-10', status: 'rejected', resume_url: '#' }
        ];

        function getApplicationsState() {
            const saved = sessionStorage.getItem('user_kanban_applications');
            if (saved) {
                try { return JSON.parse(saved); } catch (_) {}
            }
            return null;
        }

        function saveApplicationsState(apps) {
            sessionStorage.setItem('user_kanban_applications', JSON.stringify(apps));
        }

        document.addEventListener('DOMContentLoaded', async () => {
            await redirectIfNotLoggedIn('user');
            renderNavbar('dashboard');
            renderFooter();
            
            const user = getLoggedInUser();
            if (user) {
                document.getElementById('dash-user-name').textContent = user.name || 'User';
            }
            
            await initApplicationsList();
        });

        document.getElementById('applications-list-body')?.addEventListener('click', (event) => {
            const card = event.target.closest('[data-application-id]');
            if (card) selectApplication(Number(card.dataset.applicationId));
        });

        async function initApplicationsList() {
            const cachedApps = getApplicationsState();
            const { ok, data } = await apiGetMyApplications();
            let apps;

            if (ok) {
                const applications = data?.applications || [];
                if (applications.length) {
                    apps = applications.map(app => ({
                        id:           app.id,
                        position:     app.job?.title   || app.job_title   || 'Unknown Position',
                        company:      app.job?.company_name || app.company_name || 'Unknown Company',
                        applied_date: app.applied_at   || app.created_at  || '',
                        status:       app.status        || 'applied',
                        resume_url:   app.resume_url || '#'
                    }));
                    saveApplicationsState(apps);
                } else {
                    apps = [];
                }
            } else {
                apps = cachedApps || fallbackApps;
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

            if (apps.length === 0) {
                container.innerHTML = `<div class="dashboard-style-30c129">You haven't applied to any jobs yet. <a href="../jobs/listing.html" class="dashboard-style-61fc2b">Browse Jobs →</a></div>`;
                return;
            }

            container.innerHTML = apps.map(app => {
                const badgeInfo = getStatusBadgeInfo(app.status);
                const safeName = escHtml(app.position);
                const safeCompany = escHtml(app.company);
                const appliedDate = app.applied_date ? timeAgo(app.applied_date) : 'Recently';
                const isActive = activeAppId === app.id;
                
                const border = isActive ? 'border: 2px solid #111827;' : 'border: 1px solid #E5E7EB;';
                const padding = isActive ? 'padding: 19px;' : 'padding: 20px;'; // Adjust padding to avoid layout shift when border thickens

                return `
                <div data-application-id="${app.id}" class="dashboard-app-card" style="${border} ${padding}">
                    <div>
                        <h4 class="dashboard-style-91f8e7">${safeName}</h4>
                        <div class="dashboard-style-49802d">
                            ${safeCompany} &nbsp;•&nbsp; ${escHtml(app.job?.location || 'San Francisco, CA')}
                        </div>
                    </div>
                    <div class="dashboard-style-7851db">
                        <div class="dashboard-style-69a86b">Applied<br>${appliedDate}</div>
                        <span class="dashboard-badge" style="background: ${badgeInfo.bg}; color: ${badgeInfo.color};">${badgeInfo.text}</span>
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
            renderList(globalAppsList); // Re-render to highlight active card

            const app = globalAppsList.find(a => a.id === id);
            if (!app) return;

            const pane = document.getElementById('job-detail-pane');
            const grid = document.getElementById('main-content-grid');
            pane.style.display = 'block';
            grid.style.gridTemplateColumns = '1fr 1.3fr';

            document.getElementById('detail-title').textContent = app.position;
            document.getElementById('detail-type').textContent = app.job?.job_type || 'Full-time';
            document.getElementById('detail-location').textContent = app.job?.location || 'San Francisco / Remote';
            document.getElementById('detail-salary').textContent = app.job?.salary || '$140k - $185k / year';

            // Format description if provided from backend
            let desc = app.job?.description || `
                <h3 class="dashboard-style-663a30">About the Role</h3>
                <p class="dashboard-style-dc2cb2">InnovateX Labs is looking for a ${escHtml(app.position)} to help us revolutionize how developers build and maintain cloud infrastructure. We are a fast-growing team tackling complex technical challenges with an unwavering focus on simplicity and elegance.</p>
                <p class="dashboard-style-91e2ae">In this role, you will lead the design strategy for our core dashboard, working closely with engineering and product partners to translate intricate technical requirements into intuitive, high-impact experiences.</p>
                
                <h3 class="dashboard-style-663a30">Key Responsibilities</h3>
                <ul class="dashboard-style-390068">
                    <li class="dashboard-style-ccd7dd">Lead design initiatives from concept to launch for our core platform features.</li>
                    <li class="dashboard-style-ccd7dd">Conduct user research and translate insights into actionable design improvements.</li>
                    <li class="dashboard-style-ccd7dd">Build and maintain a scalable design system that supports consistent product experiences.</li>
                </ul>

                <h3 class="dashboard-style-663a30">What We're Looking For</h3>
                <p>5+ years of experience in product design, preferably in B2B SaaS or developer tools.</p>
            `;

            if (app.job?.description) {
                // Extremely basic parsing for user-submitted descriptions to add styling
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

        function getStatusBadgeInfo(status) {
            const s = (status || 'applied').toLowerCase();
            if (s.includes('review') || s === 'applied') return { bg: '#DBEAFE', color: '#1D4ED8', text: 'In Review' };
            if (s.includes('shortlisted') || s.includes('interview')) return { bg: '#D1FAE5', color: '#047857', text: 'Interviewing' };
            if (s.includes('reject')) return { bg: '#FEE2E2', color: '#B91C1C', text: 'Rejected' };
            if (s.includes('offer') || s.includes('hire')) return { bg: '#111827', color: '#ffffff', text: 'Offer Received' };
            return { bg: '#F3F4F6', color: '#374151', text: 'Applied' };
        }

        function escHtml(str) {
            const d = document.createElement('div');
            d.textContent = str || '';
            return d.innerHTML;
        }
