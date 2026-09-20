"""Unit tests for the Resume Intelligence foundation."""

import unittest
from datetime import date

from career_profile.models import CareerProfile, WorkExperience
from core.exceptions import ValidationError
from resume_intelligence import (
    Resume,
    ResumeBuilder,
    ResumeEntry,
    ResumeParser,
    ResumeSection,
    ResumeService,
    ResumeVersionManager,
)
from resume_intelligence.schemas import validate_resume


def resume_data(**overrides):
    data = {
        "resume_id": "resume-1",
        "full_name": "Ada Lovelace",
        "email": "ada@example.com",
        "summary": "Engineer",
        "skills": ["Python"],
        "sections": [
            {
                "name": "Experience",
                "entries": [{"title": "Engineer", "content": "Acme"}],
            }
        ],
    }
    data.update(overrides)
    return data


def career_profile():
    return CareerProfile(
        profile_id="profile-1",
        full_name="Ada Lovelace",
        email="ada@example.com",
        professional_summary="Verified engineer.",
        work_experience=(
            WorkExperience(
                employer="Acme",
                job_title="Engineer",
                start_date=date(2020, 1, 1),
                skills=("Python",),
            ),
        ),
        skills=("Python",),
    )


class ResumeTests(unittest.TestCase):
    def test_valid_resume_creation(self):
        resume = validate_resume(resume_data())
        self.assertEqual(resume.resume_id, "resume-1")
        self.assertEqual(resume.sections[0].entries[0].title, "Engineer")

    def test_invalid_required_fields(self):
        for field in ("resume_id", "full_name", "email"):
            with self.subTest(field=field):
                with self.assertRaises(ValidationError):
                    validate_resume(resume_data(**{field: ""}))

    def test_invalid_collection_types(self):
        with self.assertRaises(ValidationError):
            validate_resume(resume_data(skills="Python"))
        with self.assertRaises(ValidationError):
            validate_resume(resume_data(sections="Experience"))

    def test_invalid_section_and_entry_types(self):
        with self.assertRaises(ValidationError):
            validate_resume(resume_data(sections=["Experience"]))
        with self.assertRaises(ValidationError):
            validate_resume(resume_data(sections=[{"name": "Experience", "entries": ["bad"]}]))

    def test_models_are_immutable(self):
        resume = validate_resume(resume_data())
        with self.assertRaises((AttributeError, TypeError)):
            resume.full_name = "Changed"
        self.assertIsInstance(resume.sections, tuple)
        self.assertIsInstance(resume.sections[0].entries, tuple)

    def test_builder_preserves_career_profile_facts(self):
        resume = ResumeBuilder().build_from_profile(career_profile())
        self.assertEqual(resume.full_name, "Ada Lovelace")
        self.assertEqual(resume.email, "ada@example.com")
        self.assertEqual(resume.skills, ("Python",))
        self.assertEqual(resume.sections[1].entries[0].content, "Acme")

    def test_builder_handles_empty_optional_sections(self):
        profile = CareerProfile("p", "Ada", "ada@example.com")
        resume = ResumeBuilder().build_from_profile(profile)
        self.assertEqual(resume.sections, ())

    def test_parser_validation(self):
        parser = ResumeParser()
        self.assertEqual(parser.parse(resume_data()).resume_id, "resume-1")
        with self.assertRaises(ValidationError):
            parser.parse("")
        with self.assertRaises(ValidationError):
            parser.parse({"resume_id": "resume-1"})

    def test_version_creation_and_numbering(self):
        manager = ResumeVersionManager()
        resume = validate_resume(resume_data())
        first = manager.create_version(resume)
        second = manager.create_version(resume)
        self.assertEqual((first.version_number, second.version_number), (1, 2))
        self.assertEqual(manager.get_version(first.version_id), first)

    def test_previous_versions_remain_unchanged(self):
        manager = ResumeVersionManager()
        first_resume = validate_resume(resume_data(summary="First"))
        second_resume = validate_resume(resume_data(summary="Second"))
        first = manager.create_version(first_resume)
        manager.create_version(second_resume)
        self.assertEqual(first.snapshot.summary, "First")
        self.assertEqual(len(manager.get_versions("resume-1")), 2)

    def test_duplicate_and_invalid_versions_are_rejected(self):
        manager = ResumeVersionManager()
        resume = validate_resume(resume_data())
        manager.create_version(resume, version_number=1)
        with self.assertRaises(ValidationError):
            manager.create_version(resume, version_number=1)
        with self.assertRaises(ValidationError):
            manager.create_version(resume, version_number=0)

    def test_service_orchestration(self):
        service = ResumeService()
        resume = service.create_resume(resume_data())
        self.assertIs(service.get_resume(resume.resume_id), resume)
        version = service.create_version(resume)
        self.assertIs(service.get_version(version.version_id), version)
        built = service.build_from_career_profile(career_profile())
        self.assertIs(service.get_resume(built.resume_id), built)


if __name__ == "__main__":
    unittest.main()
