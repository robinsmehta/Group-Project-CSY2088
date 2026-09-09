let currentJobId = null;
        const modal = document.getElementById('apply-modal');

        document.addEventListener('DOMContentLoaded', async () => {
            renderNavbar('jobs');
            renderFooter();

            modal.style.display = 'none';

            const params = new URLSearchParams(window.location.search);
            currentJobId = params.get('id');

            if (!currentJobId) {
                document.getElementById('header-content').innerHTML = '<p class="jobs-style-fe25f4">No job ID specified.</p>';
                document.getElementById('job-content').innerHTML = '';
                document.getElementById('apply-sidebar').innerHTML = '';
                return;
            }

            const { ok, data } = await apiGetJob(currentJobId);
            const job = data?.job || null;

            if (!ok || !job || !job.id) {
                document.getElementById('header-content').innerHTML = '<p class="jobs-style-fe25f4">Job not found or has been removed.</p>';
                document.getElementById('job-content').innerHTML = '';
                document.getElementById('apply-sidebar').innerHTML = '';
                return;
            }

            renderJobDetail(job);

            const currentUser = getLoggedInUser();
            if (currentUser && currentUser.role === 'user') {
                const { ok: mok, data: mdata } = await apiGetMyApplications();
                const alreadyApplied = mok && Array.isArray(mdata.applications) &&
                    mdata.applications.some(a => String(a.job_id) === String(currentJobId));
                if (alreadyApplied) {
                    const btn = document.getElementById('open-apply-btn');
                    if (btn) {
                        btn.textContent = '✓ Already Applied';
                        btn.disabled = true;
                        btn.style.background = '#F3F4F6';
                        btn.style.color = '#111827';
                    }
                }
            }

            document.getElementById('close-modal').addEventListener('click', () => modal.style.display = 'none');
            modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });

            document.getElementById('apply-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const user = getLoggedInUser();
                if (!user || user.role !== 'user') {
                    showToast('Please log in as a job seeker to apply.', 'error');
                    setTimeout(() => window.location.href = '../auth/login.html', 1000);
                    return;
                }
                const resumeFile = document.getElementById('resume-file').files[0];
                const errDiv = document.getElementById('apply-error');
                const btn = document.getElementById('apply-submit');

                errDiv.style.display = 'none';
                btn.disabled = true;
                btn.textContent = 'Submitting…';

                const { ok: aok, data: adata } = await apiApplyToJob(currentJobId, resumeFile);

                if (aok) {
                    modal.style.display = 'none';
                    showToast('Application submitted successfully!', 'success');
                    // Update button on page
                    const mainBtn = document.getElementById('open-apply-btn');
                    if (mainBtn) {
                        mainBtn.textContent = '✓ Already Applied';
                        mainBtn.disabled = true;
                        mainBtn.style.background = '#F3F4F6';
                        mainBtn.style.color = '#111827';
                    }
                } else {
                    const msg = adata.error || adata.message || 'Failed to submit application.';
                    errDiv.textContent = msg;
                    errDiv.style.display = 'block';
                    btn.disabled = false;
                    btn.textContent = 'Submit Application';
                }
            });

            document.getElementById('resume-file').addEventListener('change', (e) => {
                document.getElementById('file-name-display').textContent = e.target.files[0] ? e.target.files[0].name : 'No file chosen';
            });
        });

        function renderJobDetail(job) {
            const esc = (s) => { const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; };
            const postedAgo = timeAgo(job.created_at);

            document.title = `Job Portal — ${job.title || 'Job Details'}`;
            document.getElementById('header-posted-date').textContent = `POSTED ${postedAgo}`;

            // Header
            document.getElementById('header-content').innerHTML = `
                <div class="jobs-style-f4b389">${esc(job.company_name || 'Unknown Company')}</div>
                <h1 class="jobs-style-2e5e62">${esc(job.title)}</h1>
                
                <div class="jobs-style-c4d0e1">
                    <div class="jobs-style-e4b265">
                        <span class="jobs-style-2567d8">JOB TYPE</span>
                        <span class="jobs-style-3d896a">${esc(job.job_type || 'Full-time')}</span>
                    </div>
                    <div class="jobs-style-e4b265">
                        <span class="jobs-style-2567d8">LOCATION</span>
                        <span class="jobs-style-3d896a">${esc(job.location || 'Not specified')}</span>
                    </div>
                    <div class="jobs-style-e4b265">
                        <span class="jobs-style-2567d8">COMPENSATION</span>
                        <span class="jobs-style-3d896a">${esc(job.salary || 'Competitive')}</span>
                    </div>
                </div>
            `;

            // Description body
            let descHtml = (job.description || '').split('\n').filter(l => l.trim()).map(l => {
                const line = esc(l.trim());
                if (line.startsWith('- ') || line.startsWith('• ')) {
                    return `<li class="jobs-style-b187d3">${line.substring(2)}</li>`;
                }
                return `<p class="jobs-style-da8c98">${line}</p>`;
            }).join('');
            
            // Extremely basic heuristic to format lists if there are any
            descHtml = descHtml.replace(/<\/li><li/g, '</li><li');
            if (descHtml.includes('<li')) {
                descHtml = descHtml.replace(/(<li.*<\/li>)/s, '<ul class="jobs-style-1d78b2">$1</ul>');
            }

            document.getElementById('job-content-card').style.display = 'block';
            document.getElementById('job-description-content').innerHTML = `
                <h3 class="jobs-style-ce9cb6">About the Role</h3>
                ${descHtml || '<p class="jobs-style-5cfcf4">No description provided.</p>'}
            `;

            document.getElementById('open-apply-btn').addEventListener('click', () => {
                const user = getLoggedInUser();
                if (!user || user.role !== 'user') {
                    showToast('Please log in as a job seeker to apply.', 'warning');
                    setTimeout(() => window.location.href = '../auth/login.html', 1000);
                    return;
                }
                modal.style.display = 'flex';
            });
        }

        function timeAgo(isoStr) {
            if (!isoStr) return 'Recently';
            const diff = Date.now() - new Date(isoStr).getTime();
            const mins = Math.floor(diff / 60000);
            if (mins < 60)  return `${mins}m ago`;
            const hrs = Math.floor(mins / 60);
            if (hrs < 24)   return `${hrs}h ago`;
            return `${Math.floor(hrs / 24)}d ago`;
        }
