def test_register_user_success(client):
    """Test successful user registration."""
    payload = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'securepassword123'
    }
    response = client.post('/api/auth/register/user', json=payload)
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'
    assert response.json['user']['name'] == 'John Doe'
    assert response.json['user']['email'] == 'john@example.com'


def test_register_user_duplicate_email(client, job_seeker):
    """Test registration with an already registered email is rejected."""
    payload = {
        'name': 'Duplicate User',
        'email': job_seeker.email,
        'password': 'password123'
    }
    response = client.post('/api/auth/register/user', json=payload)
    assert response.status_code == 409
    assert 'already registered' in response.json['error'].lower()


def test_login_wrong_password(client, job_seeker):
    """Test login with an incorrect password returns 401."""
    payload = {
        'email': job_seeker.email,
        'password': 'wrongpassword123',
        'role': 'user'
    }
    response = client.post('/api/auth/login', json=payload)
    assert response.status_code == 401
    assert 'invalid email or password' in response.json['error'].lower()


def test_access_role_required_route_without_session(client):
    """Test accessing a @role_required route without session returns 401."""
    response = client.get('/api/auth/company/test')
    assert response.status_code == 401
    assert 'authentication required' in response.json['error'].lower()
