import io
from app.models.job import Job
from app.models.application import Application


def test_apply_to_job_creates_application_row(client, job_seeker, approved_company, db):
    """Test applying to a job creates an Application row in the database."""
    job = Job(
        company_id=approved_company.id,
        title='Backend Developer',
        description='Develop Flask APIs',
        location='Remote'
    )
    db.session.add(job)
    db.session.commit()

    login_res = client.post('/api/auth/login', json={
        'email': job_seeker.email,
        'password': 'password123',
        'role': 'user'
    })
    assert login_res.status_code == 200

    data = {
        'job_id': str(job.id),
        'resume': (io.BytesIO(b'%PDF-1.4 test resume content'), 'resume.pdf')
    }
    response = client.post('/api/applications', data=data, content_type='multipart/form-data')
    assert response.status_code == 201
    assert response.json['message'] == 'Application submitted successfully'

    # Assert application record was created in the DB
    app_row = Application.query.filter_by(user_id=job_seeker.id, job_id=job.id).first()
    assert app_row is not None
    assert app_row.status == 'applied'


def test_update_application_status_invalid_status_rejected(client, job_seeker, approved_company, db):
    """Test updating application status with an invalid status is rejected with HTTP 400."""
    job = Job(company_id=approved_company.id, title='Dev', description='Desc', location='Remote')
    db.session.add(job)
    db.session.commit()

    app_record = Application(job_id=job.id, user_id=job_seeker.id, resume_path='uploads/resume.pdf', status='applied')
    db.session.add(app_record)
    db.session.commit()

    login_res = client.post('/api/auth/login', json={
        'email': approved_company.email,
        'password': 'password123',
        'role': 'company'
    })
    assert login_res.status_code == 200

    invalid_res = client.put(f'/api/applications/{app_record.id}/status', json={'status': 'invalid_status_value'})
    assert invalid_res.status_code == 400
    assert 'invalid status' in invalid_res.json['error'].lower()


def test_only_four_valid_enum_statuses_accepted(client, job_seeker, approved_company, db):
    """Test that only the 4 valid enum statuses (applied, under_review, shortlisted, rejected) are accepted."""
    job = Job(company_id=approved_company.id, title='Dev', description='Desc', location='Remote')
    db.session.add(job)
    db.session.commit()

    app_record = Application(job_id=job.id, user_id=job_seeker.id, resume_path='uploads/resume.pdf', status='applied')
    db.session.add(app_record)
    db.session.commit()

    login_res = client.post('/api/auth/login', json={
        'email': approved_company.email,
        'password': 'password123',
        'role': 'company'
    })
    assert login_res.status_code == 200

    valid_statuses = ['applied', 'under_review', 'shortlisted', 'rejected']
    for valid_status in valid_statuses:
        res = client.put(f'/api/applications/{app_record.id}/status', json={'status': valid_status})
        assert res.status_code == 200
        assert res.json['application']['status'] == valid_status

    invalid_statuses = ['interview_scheduled', 'offered', 'hired', 'unknown_status', 'fake_status']
    for invalid_status in invalid_statuses:
        res = client.put(f'/api/applications/{app_record.id}/status', json={'status': invalid_status})
        assert res.status_code == 400
        assert 'error' in res.json
