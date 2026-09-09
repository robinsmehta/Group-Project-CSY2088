document.addEventListener('DOMContentLoaded', () => {

            // Handle Pill Toggle
            const roleInput = document.getElementById('register-role');
            const companyNotice = document.getElementById('company-notice');
            const nameLabel = document.getElementById('name-label');
            const nameInput = document.getElementById('register-name');
            const submitBtnText = document.getElementById('submit-btn-text');
            const rolePills = document.querySelectorAll('.role-pill');

            rolePills.forEach(pill => {
                pill.addEventListener('click', () => {
                    rolePills.forEach(p => p.classList.remove('active'));
                    pill.classList.add('active');
                    const role = pill.getAttribute('data-role');
                    roleInput.value = role;

                    if (role === 'company') {
                        companyNotice.style.display = 'block';
                        nameLabel.textContent = 'Company Name';
                        nameInput.placeholder = 'Me';
                        submitBtnText.textContent = 'Create Employer Account';
                    } else {
                        companyNotice.style.display = 'none';
                        nameLabel.textContent = 'Name';
                        nameInput.placeholder = 'Jane';
                        submitBtnText.textContent = 'Create Seeker Account';
                    }
                });
            });

            const form = document.getElementById('register-form');
            const submitBtn = form.querySelector('.btn-submit');
            const errorBox = document.getElementById('register-error');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                errorBox.style.display = 'none';
                const name     = document.getElementById('register-name').value.trim();
                const email    = document.getElementById('register-email').value.trim();
                const password = document.getElementById('register-password').value;
                const role     = document.getElementById('register-role').value;

                submitBtn.disabled = true;
                submitBtn.querySelector('span').textContent = 'Creating account…';

                let ok, data;
                if (role === 'company') {
                    const res = await apiRegisterCompany(name, email, password, '');
                    ok = res.ok;
                    data = res.data;
                } else {
                    const res = await apiRegisterUser(name, email, password);
                    ok = res.ok;
                    data = res.data;
                }

                if (ok) {
                    const user = data.user || {};
                    const userObj = {
                        id:           user.id || null,
                        email:        user.email || email,
                        role:         user.role || role,
                        name:         user.name || user.company_name || email.split('@')[0],
                        company_name: user.company_name || null,
                        status:       user.status || null
                    };
                    setLoggedInUser(userObj);
                    showToast('Account created successfully!', 'success');
                    setTimeout(() => {
                        if (role === 'company') window.location.href = resolveSitePath('company/dashboard.html');
                        else if (role === 'admin') window.location.href = resolveSitePath('admin/dashboard.html');
                        else window.location.href = resolveSitePath('user/dashboard.html');
                    }, 600);
                } else {
                    const msg = data.error || data.message || 'Registration failed. Please try again.';
                    errorBox.textContent = msg;
                    errorBox.style.display = 'block';
                    submitBtn.disabled = false;
                    submitBtn.querySelector('span').textContent = 'Create Account';
                }
            });
        });
