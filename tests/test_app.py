"""Flask smoke and form tests; no live MySQL required."""
import unittest
from unittest.mock import patch

from app import app, validate_form


class ValidationTests(unittest.TestCase):
    def test_company_required(self):
        _, errors = validate_form('companies', {'company_name': ''})
        self.assertIn('company_name', errors)

    def test_job_requirements_are_valid_json(self):
        values, errors = validate_form('jobs', {
            'company_id': '1', 'job_title': 'Developer',
            'requirements': ' Python, SQL, Flask ', 'salary_min': '100',
            'salary_max': '150',
        })
        self.assertFalse(errors)
        self.assertEqual(values['requirements'], '["Python", "SQL", "Flask"]')

    def test_invalid_salary_and_interview_json(self):
        _, errors = validate_form('jobs', {'company_id': '1', 'job_title': 'Developer',
                                           'salary_min': '150', 'salary_max': '100'})
        self.assertIn('salary_max', errors)
        _, errors = validate_form('applications', {'job_id': '1',
                      'application_date': '2026-11-08', 'interview_data': 'oops'})
        self.assertIn('interview_data', errors)


class FlaskSmokeTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SECRET_KEY='test-secret')
        self.client = app.test_client()

    def test_dashboard_responds(self):
        def fake_query(sql, params=(), *, one=False):
            return {'n': 0} if one else []
        with patch('app.database.query', side_effect=fake_query):
            response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your career dashboard', response.data)

    def test_crud_pages_render_and_csrf_blocks_untrusted_post(self):
        with patch('app.database.query', return_value=[]):
            for entity in ('companies', 'jobs', 'applications', 'contacts'):
                self.assertEqual(self.client.get(f'/{entity}').status_code, 200)
                self.assertEqual(self.client.get(f'/{entity}/new').status_code, 200)
        response = self.client.post('/companies/new', data={'company_name': 'Example'})
        self.assertEqual(response.status_code, 400)

    def test_job_match_post_uses_ranker(self):
        with self.client.session_transaction() as sess:
            sess['_csrf_token'] = 'safe-token'
        mocked = [{'job_id': 1, 'job_title': 'Developer', 'company_name': 'TechCo',
                   'job_type': 'Full-time', 'requirements': '["Python", "SQL", "Tableau"]'}]
        with patch('app.database.query', return_value=mocked):
            response = self.client.post('/job-match', data={
                '_csrf_token': 'safe-token', 'skills': 'Python, SQL, Flask'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'67%', response.data)
        self.assertIn(b'Tableau', response.data)


if __name__ == '__main__':
    unittest.main()
