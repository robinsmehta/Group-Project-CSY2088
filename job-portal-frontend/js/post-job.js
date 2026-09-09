async function loadJobData(jobId) {
            const { ok, data } = await apiGetJob(jobId);
            const job = data?.job;
            if (!ok || !job) {
                const error = document.getElementById('post-job-error');
                error.textContent = data?.error || 'Failed to load the job.';
                error.style.display = 'block';
                return;
            }

            document.getElementById('job-title').value = job.title || '';
            document.getElementById('job-category').value = job.category || '';
            document.getElementById('job-type').value = job.job_type || '';
            document.getElementById('job-location').value = job.location || '';
            document.getElementById('job-salary').value = job.salary || '';
            document.getElementById('job-description').value = job.description || '';
            if (job.closing_date) {
                document.getElementById('job-closing-date').value = job.closing_date.slice(0, 16);
            }
        }

        document.addEventListener('DOMContentLoaded', async () => {
            await redirectIfNotLoggedIn('company');
            renderNavbar('post-job');
            renderFooter();

            const urlParams = new URLSearchParams(window.location.search);
            const jobId = urlParams.get('id');
            const isEditMode = !!jobId;
            const submitBtn = document.getElementById('submit-btn');
            const pageTitle = document.getElementById('page-title');
            const btnDelete = document.getElementById('btn-delete-job');

            btnDelete.addEventListener('click', async () => {
                if (!isEditMode || !window.confirm('Delete this job posting? This cannot be undone.')) {
                    return;
                }

                btnDelete.disabled = true;
                btnDelete.textContent = 'Deleting…';
                const { ok, data } = await apiDeleteJob(jobId);

                if (ok) {
                    showToast('Job deleted successfully.', 'success');
                    setTimeout(() => {
                        window.location.href = resolveSitePath('company/dashboard.html');
                    }, 800);
                } else {
                    const error = document.getElementById('post-job-error');
                    error.textContent = data?.error || 'Failed to delete the job.';
                    error.style.display = 'block';
                    btnDelete.disabled = false;
                    btnDelete.textContent = 'Delete Job';
                }
            });

            if (isEditMode) {
                pageTitle.textContent = 'Edit Post';
                submitBtn.textContent = 'Edit Job';
                btnDelete.style.display = 'inline-block';
                await loadJobData(jobId);
            } else {
                // const { ok, data } = await apiGetJob(jobId);
                // if (ok && data.job) { populate fields here... }
            }

            // Skills Tag Logic (TASK-021)
            const skillsInput = document.getElementById('job-skills-input');
            const skillsContainer = document.getElementById('skills-container');
            const hiddenSkills = document.getElementById('job-skills-hidden');
            let tags = [];

            function renderTags() {
                document.querySelectorAll('.skill-pill').forEach(el => el.remove());
                tags.forEach((tag, index) => {
                    const pill = document.createElement('span');
                    pill.className = 'skill-pill';
                    pill.innerHTML = `${escHtml(tag)}<span class="remove-pill" data-index="${index}">&times;</span>`;
                    skillsContainer.insertBefore(pill, skillsInput);
                });
                hiddenSkills.value = tags.join(', ');
            }

            skillsContainer.addEventListener('click', (e) => {
                if (e.target.classList.contains('remove-pill')) {
                    const idx = parseInt(e.target.getAttribute('data-index'), 10);
                    tags.splice(idx, 1);
                    renderTags();
                }
            });

            skillsInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ',') {
                    e.preventDefault();
                    const val = skillsInput.value.trim().replace(/^,|,$/g, '').trim();
                    if (val && !tags.includes(val)) {
                        tags.push(val);
                        renderTags();
                    }
                    skillsInput.value = '';
                }
            });

            function escHtml(str) {
                const d = document.createElement('div');
                d.textContent = str || '';
                return d.innerHTML;
            }

            // Form Submission
            const form = document.getElementById('post-job-form');
            const errDiv = document.getElementById('post-job-error');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                errDiv.style.display = 'none';

                const title       = document.getElementById('job-title').value.trim();
                const category    = document.getElementById('job-category').value;
                const job_type    = document.getElementById('job-type').value;
                const location    = document.getElementById('job-location').value.trim();
                const salary      = document.getElementById('job-salary').value.trim();
                const description = document.getElementById('job-description').value.trim();
                const closing_date = (document.getElementById('job-closing-date').value || '').trim() || null;
                const skills      = hiddenSkills.value;

                submitBtn.disabled = true;
                submitBtn.textContent = isEditMode ? 'Saving…' : 'Publishing…';

                let ok, data;
                if (isEditMode) {
                    const res = await apiUpdateJob(jobId, {
                        title,
                        category,
                        job_type,
                        location,
                        salary,
                        description,
                        closing_date
                    });
                    ok = res.ok;
                    data = res.data;
                } else {
                    const res = await apiCreateJob({ title, category, job_type, location, salary, description, closing_date });
                    ok = res.ok; data = res.data;
                }

                if (ok) {
                    showToast(isEditMode ? 'Job updated successfully!' : 'Job posted successfully!', 'success');
                    setTimeout(() => { window.location.href = resolveSitePath('company/dashboard.html'); }, 1000);
                } else {
                    errDiv.textContent = data.error || data.message || 'Failed to process request.';
                    errDiv.style.display = 'block';
                    submitBtn.disabled = false;
                    submitBtn.textContent = isEditMode ? 'Edit Job' : 'Publish Job';
                }
            });
        });
