import io
from app.models.admin import Admin
from flask_bcrypt import generate_password_hash


def test_end_to_end_job_application_flow(client, db):
    """
    ONE end-to-end integration test flow:
    register seeker -> register company -> admin approves company ->
    company posts job -> seeker applies -> company shortlists ->
    seeker's application list shows status 'shortlisted'.
    """
    # 1. Register Seeker
    reg_seeker_res = client.post('/api/auth/register/user', json={
        'name': 'Seeker User',
        'email': 'seeker@example.com',
        'password': 'seekerpassword123'
    })
    assert reg_seeker_res.status_code == 201
    assert reg_seeker_res.json['message'] == 'User registered successfully'
    assert reg_seeker_res.json['user']['email'] == 'seeker@example.com'

    # 2. Register Company (starts as pending)
    reg_company_res = client.post('/api/auth/register/company', json={
        'company_name': 'Tech Corp',
        'email': 'hr@techcorp.com',
        'password': 'companypassword123',
        'description': 'Innovative Tech Company'
    })
    assert reg_company_res.status_code == 201
    assert 'pending' in reg_company_res.json['company']['status']
    company_id = reg_company_res.json['company']['id']

    # 3. Admin Approves Company
    admin = Admin(
        name='Super Admin',
        email='admin@hirehub.com',
        password_hash=generate_password_hash('admin123').decode('utf-8')
    )
    db.session.add(admin)
    db.session.commit()

    admin_login_res = client.post('/api/auth/login', json={
        'email': 'admin@hirehub.com',
        'password': 'admin123',
        'role': 'admin'
    })
    assert admin_login_res.status_code == 200
    assert admin_login_res.json['role'] == 'admin'

    approve_res = client.put(f'/api/admin/companies/{company_id}/approve')
    assert approve_res.status_code == 200
    assert approve_res.json['message'] == 'Company approved successfully'
    assert approve_res.json['company']['status'] == 'approved'

    # 4. Company Posts Job
    comp_login_res = client.post('/api/auth/login', json={
        'email': 'hr@techcorp.com',
        'password': 'companypassword123',
        'role': 'company'
    })
    assert comp_login_res.status_code == 200
    assert comp_login_res.json['role'] == 'company'

    job_payload = {
        'title': 'Fullstack Engineer',
        'description': 'Build modern web applications',
        'location': 'Remote',
        'category': 'Engineering',
        'salary': '$110,000',
        'skills': 'Python, JavaScript'
    }
    job_res = client.post('/api/jobs', json=job_payload)
    assert job_res.status_code == 201
    assert job_res.json['message'] == 'Job created successfully'
    job_id = job_res.json['job']['id']

    # 5. Seeker Applies
    seeker_login_res = client.post('/api/auth/login', json={
        'email': 'seeker@example.com',
        'password': 'seekerpassword123',
        'role': 'user'
    })
    assert seeker_login_res.status_code == 200
    assert seeker_login_res.json['role'] == 'user'

    apply_data = {
        'job_id': str(job_id),
        'resume': (io.BytesIO(b'%PDF-1.4 test resume content'), 'my_resume.pdf')
    }
    apply_res = client.post('/api/applications', data=apply_data, content_type='multipart/form-data')
    assert apply_res.status_code == 201
    assert apply_res.json['message'] == 'Application submitted successfully'
    app_id = apply_res.json['application']['id']

    # 6. Company Shortlists Application
    comp_login_res2 = client.post('/api/auth/login', json={
        'email': 'hr@techcorp.com',
        'password': 'companypassword123',
        'role': 'company'
    })
    assert comp_login_res2.status_code == 200

    shortlist_res = client.put(f'/api/applications/{app_id}/status', json={'status': 'shortlisted'})
    assert shortlist_res.status_code == 200
    assert shortlist_res.json['message'] == 'Application status updated successfully'
    assert shortlist_res.json['application']['status'] == 'shortlisted'

    # 7. Seeker's Application List Shows Status 'shortlisted'
    seeker_login_res2 = client.post('/api/auth/login', json={
        'email': 'seeker@example.com',
        'password': 'seekerpassword123',
        'role': 'user'
    })
    assert seeker_login_res2.status_code == 200

    mine_res = client.get('/api/applications/mine')
    assert mine_res.status_code == 200
    applications = mine_res.json.get('applications', [])
    assert len(applications) > 0

    target_app = next((a for a in applications if a['id'] == app_id), None)
    assert target_app is not None
    assert target_app['status'] == 'shortlisted'
    assert target_app['job_title'] == 'Fullstack Engineer'
