import unittest
from matching import rank_jobs, requirement_skills, skills_from_text


class MatchTests(unittest.TestCase):
    def test_skills_normalized_and_deduplicated(self):
        self.assertEqual(skills_from_text(' Python, SQL ,python,, Flask '),
                         ['Python', 'SQL', 'Flask'])

    def test_requirements_json_string_or_dict(self):
        self.assertEqual(requirement_skills('["Python", "SQL"]'), ['Python', 'SQL'])
        self.assertEqual(requirement_skills({'skills': ['Flask']}), ['Flask'])
        self.assertEqual(requirement_skills('not json'), [])

    def test_ranking_and_missing_skills(self):
        jobs = [
            {'job_id': 1, 'job_title': 'Analyst', 'requirements': '["Python", "SQL", "Tableau"]'},
            {'job_id': 2, 'job_title': 'Developer', 'requirements': '["Python", "SQL", "Flask"]'},
            {'job_id': 3, 'job_title': 'Unknown', 'requirements': None},
        ]
        ranked = rank_jobs(jobs, skills_from_text('python,SQL,Flask'))
        self.assertEqual([j['job_id'] for j in ranked], [2, 1, 3])
        self.assertEqual(ranked[0]['percentage'], 100)
        self.assertEqual(ranked[1]['percentage'], 67)
        self.assertEqual(ranked[1]['missing_skills'], ['Tableau'])
        self.assertIsNone(ranked[2]['percentage'])


if __name__ == '__main__':
    unittest.main()
