import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app import create_app
from app.models.application import Application


class FakeApplicationQuery:
    def __init__(self, application):
        self.application = application

    def filter(self, _condition):
        return self

    def first(self):
        return self.application


class ResumeDownloadTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app = create_app('default')
        self.app.config.update(
            TESTING=True,
            SECRET_KEY='test-secret',
            UPLOAD_FOLDER=self.temp_dir.name,
        )
        self.client = self.app.test_client()
        self.filename = 'resume.pdf'
        Path(self.temp_dir.name, self.filename).write_bytes(b'resume')

    def tearDown(self):
        self.temp_dir.cleanup()

    def set_session(self, user_id, role, company_id=None):
        with self.client.session_transaction() as session:
            session['user_id'] = user_id
            session['role'] = role
            if company_id is not None:
                session['company_id'] = company_id

    def application(self, user_id=7, company_id=11):
        return SimpleNamespace(
            user_id=user_id,
            job=SimpleNamespace(company_id=company_id),
        )

    def test_requires_authentication(self):
        response = self.client.get(
            f'/api/applications/resumes/{self.filename}'
        )

        self.assertEqual(response.status_code, 401)

    def test_allows_applicant_and_owning_company(self):
        application = self.application()
        with self.app.app_context(), patch.object(
            Application, 'query', FakeApplicationQuery(application)
        ):
            self.set_session(user_id=7, role='user')
            applicant_response = self.client.get(
                f'/api/applications/resumes/{self.filename}'
            )

            self.client.post('/api/auth/logout')
            self.set_session(user_id=11, role='company', company_id=11)
            company_response = self.client.get(
                f'/api/applications/resumes/{self.filename}'
            )

        self.assertEqual(applicant_response.status_code, 200)
        self.assertEqual(company_response.status_code, 200)

    def test_rejects_unrelated_account(self):
        application = self.application()
        with self.app.app_context(), patch.object(
            Application, 'query', FakeApplicationQuery(application)
        ):
            self.set_session(user_id=8, role='user')
            response = self.client.get(
                f'/api/applications/resumes/{self.filename}'
            )

        self.assertEqual(response.status_code, 403)

    def test_returns_not_found_for_unknown_resume(self):
        self.set_session(user_id=7, role='user')
        with self.app.app_context(), patch.object(
            Application, 'query', FakeApplicationQuery(None)
        ):
            response = self.client.get(
                f'/api/applications/resumes/{self.filename}'
            )

        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()