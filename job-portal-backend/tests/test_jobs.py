from app.models.company import Company
from app.models.job import Job
from flask_bcrypt import generate_password_hash


def test_approved_company_can_create_job(client, approved_company):
    """Test that an approved company can successfully post a job listing."""
    login_res = client.post('/api/auth/login', json={
        'email': approved_company.email,
        'password': 'password123',
        'role': 'company'
    })
    assert login_res.status_code == 200

    job_data = {
        'title': 'Senior Backend Engineer',
        'description': 'Develop Flask microservices',
        'location': 'Remote',
        'category': 'Engineering',
        'salary': '$120,000',
        'job_type': 'Full-time',
        'skills': 'Python, Flask, SQL'
    }
    response = client.post('/api/jobs', json=job_data)
    assert response.status_code == 201
    assert response.json['message'] == 'Job created successfully'
    assert response.json['job']['title'] == 'Senior Backend Engineer'
    assert response.json['job']['company_id'] == approved_company.id
    assert response.json['job']['skills'] == 'Python, Flask, SQL'


def test_pending_company_cannot_create_job(client, db):
    """Test that an unapproved (pending) company cannot post a job listing."""
    pending_company = Company(
        company_name='Pending Startup',
        email='pending@startup.com',
        password_hash=generate_password_hash('password123').decode('utf-8'),
        status='pending'
    )
    db.session.add(pending_company)
    db.session.commit()

    login_res = client.post('/api/auth/login', json={
        'email': 'pending@startup.com',
        'password': 'password123',
        'role': 'company'
    })
    assert login_res.status_code == 200

    job_data = {
        'title': 'Frontend Developer',
        'description': 'Build React components',
        'location': 'Remote'
    }
    response = client.post('/api/jobs', json=job_data)
    assert response.status_code == 403
    assert 'pending admin approval' in response.json['error'].lower()


def test_company_cannot_update_or_delete_other_company_job(client, approved_company, db):
    """Test that a company cannot update or delete another company's job posting."""
    company_b = Company(
        company_name='Company B',
        email='hr@companyb.com',
        password_hash=generate_password_hash('password123').decode('utf-8'),
        status='approved'
    )
    db.session.add(company_b)

    job = Job(
        company_id=approved_company.id,
        title='Company A Job',
        description='Job description for Company A',
        location='San Francisco, CA'
    )
    db.session.add(job)
    db.session.commit()

    login_res = client.post('/api/auth/login', json={
        'email': 'hr@companyb.com',
        'password': 'password123',
        'role': 'company'
    })
    assert login_res.status_code == 200

    # Attempt to update Company A's job
    update_res = client.put(f'/api/jobs/{job.id}', json={'title': 'Unauthorized Update'})
    assert update_res.status_code == 403
    assert 'do not own' in update_res.json['error'].lower()

    # Attempt to delete Company A's job
    delete_res = client.delete(f'/api/jobs/{job.id}')
    assert delete_res.status_code == 403
    assert 'permission' in delete_res.json['error'].lower() or 'do not own' in delete_res.json['error'].lower()


def test_keyword_search_matches_skills(client, approved_company, db):
    """Test that keyword search matches skills column."""
    job = Job(
        company_id=approved_company.id,
        title='Backend Developer',
        description='General backend role',
        location='Remote',
        skills='React, Docker, Kubernetes'
    )
    db.session.add(job)
    db.session.commit()

    res = client.get('/api/jobs?keyword=Kubernetes')
    assert res.status_code == 200
    assert len(res.json['jobs']) >= 1
    assert any(j['id'] == job.id for j in res.json['jobs'])

