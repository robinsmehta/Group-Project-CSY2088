document.addEventListener('DOMContentLoaded', async () => {
            renderNavbar('home');
            renderFooter();
            await loadHomeFeaturedJobs();
        });

        async function loadHomeFeaturedJobs() {
            const grid = document.getElementById('featured-jobs-grid');
            try {
                const { ok, data } = await apiGetJobs();
                if (ok && data.jobs && data.jobs.length > 0) {
                    const jobs = data.jobs.slice(0, 4);
                    grid.innerHTML = jobs.map(job => {
                        const company  = job.company_name || 'Unknown Company';
                        const location = job.location || '';
                        const salary   = job.salary || '—';
                        const type     = job.job_type || 'Full-time';
                        const timeStr  = timeAgo(job.created_at);
                        return `
                            <a href="jobs/detail.html?id=${job.id}" class="job-card">
                                <h3>${escHtml(job.title)}</h3>
                                <p class="job-card-company">${escHtml(company)}<br>${location ? escHtml(location) : ''}</p>
                                <div class="job-card-type-wrapper">
                                    <span class="job-card-type">${escHtml(type)}</span>
                                </div>
                                <div class="job-card-footer">
                                    <span class="job-card-salary">${escHtml(salary)}</span>
                                    <span class="job-card-date">
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                                        ${timeStr}
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" class="icon-ml-8"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                                    </span>
                                </div>
                            </a>
                        `;
                    }).join('');
                }
            } catch (e) {
                console.error('Failed to load jobs:', e);
            }
        }

        function escHtml(str) {
            const d = document.createElement('div');
            d.textContent = str || '';
            return d.innerHTML;
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
