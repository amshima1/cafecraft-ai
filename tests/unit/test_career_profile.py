"""Unit tests for the Career Profile foundation."""

import unittest
from datetime import date

from core.exceptions import ValidationError
from career_profile import CareerProfileService, InMemoryCareerProfileRepository
from career_profile.models import CareerProfile, WorkExperience
from career_profile.schemas import validate_profile


def profile_data(**overrides):
    data = {
        "profile_id": "profile-1",
        "full_name": "Ada Lovelace",
        "email": "ada@example.com",
        "work_experience": [
            {
                "employer": "Analytical Engines Ltd",
                "job_title": "Engineer",
                "start_date": "2020-01-01",
                "skills": ["Python"],
            }
        ],
        "education": [
            {"institution": "University", "degree": "BSc", "end_date": "2019-06-01"}
        ],
    }
    data.update(overrides)
    return data


class CareerProfileTests(unittest.TestCase):
    def setUp(self):
        self.repository = InMemoryCareerProfileRepository()
        self.service = CareerProfileService(self.repository)

    def test_valid_profile_creation(self):
        profile = self.service.create_profile(profile_data())
        self.assertIsInstance(profile, CareerProfile)
        self.assertEqual(profile.email, "ada@example.com")
        self.assertEqual(profile.work_experience[0].start_date, date(2020, 1, 1))

    def test_invalid_required_fields(self):
        for field in ("profile_id", "full_name", "email"):
            with self.subTest(field=field):
                data = profile_data(**{field: ""})
                with self.assertRaises(ValidationError):
                    self.service.create_profile(data)

    def test_invalid_email(self):
        with self.assertRaises(ValidationError):
            self.service.create_profile(profile_data(email="not-an-email"))

    def test_work_experience_validation(self):
        with self.assertRaises(ValidationError):
            self.service.create_profile(profile_data(work_experience=[{"employer": "", "job_title": "Engineer", "start_date": "2020-01-01"}]))
        with self.assertRaises(ValidationError):
            self.service.create_profile(profile_data(work_experience=[{"employer": "Acme", "job_title": "Engineer", "start_date": "bad-date"}]))

    def test_education_validation(self):
        with self.assertRaises(ValidationError):
            self.service.create_profile(profile_data(education=[{"institution": "", "degree": "BSc"}]))

    def test_profile_update(self):
        self.service.create_profile(profile_data())
        updated = self.service.update_profile("profile-1", profile_data(full_name="Grace Hopper"))
        self.assertEqual(updated.full_name, "Grace Hopper")

    def test_profile_retrieval_and_deletion(self):
        self.service.create_profile(profile_data())
        self.assertIsNotNone(self.service.get_profile("profile-1"))
        self.service.delete_profile("profile-1")
        self.assertIsNone(self.service.get_profile("profile-1"))

    def test_repository_behavior(self):
        profile = validate_profile(profile_data())
        self.repository.save(profile)
        self.assertEqual(self.repository.get(profile.profile_id), profile)
        with self.assertRaises(ValidationError):
            self.repository.save(profile)
        replacement = CareerProfile(profile_id=profile.profile_id, full_name="Grace Hopper", email="grace@example.com")
        self.assertEqual(self.repository.update(replacement), replacement)
        self.repository.delete(profile.profile_id)
        self.assertIsNone(self.repository.get(profile.profile_id))

    def test_service_repository_separation(self):
        class SpyRepository(InMemoryCareerProfileRepository):
            def save(self, profile):
                self.saved = profile
                return super().save(profile)

        repository = SpyRepository()
        service = CareerProfileService(repository)
        service.create_profile(profile_data())
        self.assertEqual(repository.saved.profile_id, "profile-1")

    def test_invalid_collection_and_entry_types(self):
        with self.assertRaises(ValidationError):
            self.service.create_profile(profile_data(skills="Python"))
        with self.assertRaises(ValidationError):
            self.service.create_profile(profile_data(work_experience=["not an object"]))

    def test_immutable_models(self):
        profile = validate_profile(profile_data())
        with self.assertRaises((AttributeError, TypeError)):
            profile.full_name = "Changed"
        self.assertIsInstance(profile.work_experience[0], WorkExperience)


if __name__ == "__main__":
    unittest.main()
