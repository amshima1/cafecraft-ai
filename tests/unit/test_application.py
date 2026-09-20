"""Unit tests for the Application Composition foundation."""

import importlib
import os
import sys
import unittest
from unittest.mock import patch

from application import ApplicationContainer
from application_workspace import ApplicationWorkspaceService
from career_profile import CareerProfileService, InMemoryCareerProfileRepository
from documents import DocumentService
from interview_intelligence import InterviewIntelligenceService
from privacy import PrivacyService
from resume_intelligence import ResumeService
from storage import StorageService
from truth_layer import Evidence, TruthLayerService


class FalsyResumeService(ResumeService):
    """A valid injected service whose truth value is deliberately false."""

    def __bool__(self) -> bool:
        return False


class ApplicationCompositionTests(unittest.TestCase):
    def test_default_container_constructs_without_ai_configuration(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            container = ApplicationContainer()
        self.assertIsNone(container.jobs)

    def test_default_capabilities_have_expected_types(self) -> None:
        container = ApplicationContainer()
        self.assertIsInstance(container.career_profiles, CareerProfileService)
        self.assertIsInstance(container.resumes, ResumeService)
        self.assertIsNone(container.jobs)
        self.assertIsInstance(container.applications, ApplicationWorkspaceService)
        self.assertIsInstance(container.interviews, InterviewIntelligenceService)
        self.assertIsInstance(container.truth, TruthLayerService)
        self.assertIsInstance(container.privacy, PrivacyService)
        self.assertIsInstance(container.documents, DocumentService)
        self.assertIsInstance(container.storage, StorageService)

    def test_injected_services_are_preserved_by_identity(self) -> None:
        services = {
            "career_profiles": CareerProfileService(InMemoryCareerProfileRepository()),
            "resumes": ResumeService(),
            "applications": ApplicationWorkspaceService(),
            "interviews": InterviewIntelligenceService(),
            "truth": TruthLayerService(),
            "privacy": PrivacyService(),
            "documents": DocumentService(),
            "storage": StorageService[object](),
        }
        container = ApplicationContainer(**services)
        for name, service in services.items():
            with self.subTest(name=name):
                self.assertIs(getattr(container, name), service)

    def test_falsy_injected_service_is_preserved_by_identity(self) -> None:
        service = FalsyResumeService()
        self.assertFalse(service)
        self.assertIs(ApplicationContainer(resumes=service).resumes, service)

    def test_explicit_job_service_is_preserved(self) -> None:
        from job_intelligence import JobIntelligenceService

        job_service = JobIntelligenceService.__new__(JobIntelligenceService)
        self.assertIs(ApplicationContainer(jobs=job_service).jobs, job_service)

    def test_default_containers_have_distinct_services(self) -> None:
        first = ApplicationContainer()
        second = ApplicationContainer()
        for name in (
            "career_profiles",
            "resumes",
            "applications",
            "interviews",
            "truth",
            "privacy",
            "documents",
            "storage",
        ):
            with self.subTest(name=name):
                self.assertIsNot(getattr(first, name), getattr(second, name))

    def test_storage_state_is_isolated(self) -> None:
        first = ApplicationContainer()
        second = ApplicationContainer()
        first.storage.save("key", "value")
        self.assertIsNone(second.storage.get("key"))

    def test_privacy_state_is_isolated(self) -> None:
        first = ApplicationContainer()
        second = ApplicationContainer()
        first.privacy.grant_consent("user-1", "resume", "t1")
        self.assertFalse(second.privacy.has_consent("user-1", "resume"))

    def test_truth_state_is_isolated(self) -> None:
        first = ApplicationContainer()
        second = ApplicationContainer()
        evidence = Evidence("e1", "profile", "p1", "verified fact", True)
        first.truth.add_evidence(evidence)
        self.assertIsNone(second.truth.get_evidence("e1"))

    def test_career_profile_state_is_isolated(self) -> None:
        first = ApplicationContainer()
        second = ApplicationContainer()
        profile = {
            "profile_id": "p1",
            "full_name": "Ada Lovelace",
            "email": "ada@example.com",
        }
        first.career_profiles.create_profile(profile)
        self.assertIsNone(second.career_profiles.get_profile("p1"))

    def test_application_state_is_isolated(self) -> None:
        first = ApplicationContainer()
        second = ApplicationContainer()
        first.applications.create(
            {
                "application_id": "a1",
                "company": "Acme",
                "job_title": "Engineer",
                "status": "applied",
                "date_applied": "2026-09-20",
            }
        )
        self.assertIsNone(second.applications.get("a1"))

    def test_interview_state_is_isolated(self) -> None:
        first = ApplicationContainer()
        second = ApplicationContainer()
        first.interviews.create_session({"session_id": "s1", "question_id": "q1"})
        self.assertIsNone(second.interviews.get_session("s1"))

    def test_default_construction_does_not_construct_ai_or_network_client(self) -> None:
        with patch("ai.client.DeepSeekClient", side_effect=AssertionError("constructed")):
            with patch("urllib.request.urlopen", side_effect=AssertionError("called")):
                container = ApplicationContainer()
        self.assertIsNone(container.jobs)

    def test_construction_has_no_document_privacy_or_storage_side_effects(self) -> None:
        container = ApplicationContainer()
        self.assertFalse(container.storage.exists("created-during-construction"))
        self.assertFalse(container.privacy.has_consent("user", "purpose"))
        self.assertEqual(
            container.documents.generate("resume", "content").content,
            "content",
        )

    def test_public_exports_only_application_container(self) -> None:
        module = importlib.import_module("application")
        self.assertEqual(module.__all__, ["ApplicationContainer"])
        self.assertEqual(
            {name for name in module.__dict__ if not name.startswith("_")},
            {"ApplicationContainer"},
        )

    def test_no_application_service_or_service_module_exists(self) -> None:
        self.assertNotIn("ApplicationService", vars(importlib.import_module("application")))
        self.assertFalse(os.path.exists(os.path.join("application", "service.py")))

    def test_no_global_container_registry_is_created(self) -> None:
        module = importlib.import_module("application.container")
        self.assertFalse(any(value is ApplicationContainer for value in module.__dict__.values()))
        self.assertFalse(any(name.endswith("_CONTAINER") for name in module.__dict__))

    def test_application_container_has_no_external_architecture_imports(self) -> None:
        source = open("application/container.py", encoding="utf-8").read()
        for forbidden in (
            "streamlit",
            "sqlalchemy",
            "sqlite3",
            "requests",
            "urllib.request",
            "DeepSeekClient",
            "DEEPSEEK_API_KEY",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)
        self.assertNotIn("._", source)

    def test_explicit_constructor_dependency_exceptions_are_not_hidden(self) -> None:
        class FailingService:
            pass

        with patch("application.container.ResumeService", side_effect=RuntimeError("failure")):
            with self.assertRaisesRegex(RuntimeError, "failure"):
                ApplicationContainer()


if __name__ == "__main__":
    unittest.main()
