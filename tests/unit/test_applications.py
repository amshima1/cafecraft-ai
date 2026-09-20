"""Unit tests for the Application Workspace foundation."""

import unittest
from datetime import date

from core.exceptions import ValidationError
from application_workspace import (
    ApplicationAnalytics,
    ApplicationWorkspaceService,
    FollowUpMessageGenerator,
    FollowUpService,
)
from application_workspace.models import Application
from application_workspace.schemas import validate_application
from application_workspace.tracker import InMemoryApplicationTracker


def application_data(**overrides):
    data = {
        "application_id": "app-1",
        "company": "Acme",
        "job_title": "Engineer",
        "job_url": "https://example.com/job",
        "status": "applied",
        "date_applied": "2026-09-20",
        "follow_up_date": "2026-09-27",
    }
    data.update(overrides)
    return data


class ApplicationWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tracker = InMemoryApplicationTracker()
        self.service = ApplicationWorkspaceService(self.tracker)

    def test_valid_creation_and_retrieval(self):
        application = self.service.create(application_data())
        self.assertEqual(application.date_applied, date(2026, 9, 20))
        self.assertIs(self.service.get("app-1"), application)

    def test_required_fields_and_status(self):
        for field in ("application_id", "company", "job_title"):
            with self.subTest(field=field), self.assertRaises(ValidationError):
                validate_application(application_data(**{field: ""}))
        with self.assertRaises(ValidationError):
            validate_application(application_data(status="unknown"))

    def test_invalid_dates_and_collections(self):
        with self.assertRaises(ValidationError):
            validate_application(application_data(date_applied="not-a-date"))
        with self.assertRaises(ValidationError):
            validate_application([])

    def test_immutable_model(self):
        application = validate_application(application_data())
        with self.assertRaises((AttributeError, TypeError)):
            application.company = "Other"

    def test_tracker_update_delete_and_status(self):
        self.service.create(application_data())
        updated = self.service.update({**application_data(), "notes": "Updated"})
        self.assertEqual(updated.notes, "Updated")
        changed = self.service.update_status("app-1", "interview")
        self.assertEqual(changed.status, "interview")
        self.service.delete("app-1")
        self.assertIsNone(self.service.get("app-1"))

    def test_duplicate_and_missing_tracker_records(self):
        application = validate_application(application_data())
        self.tracker.create(application)
        with self.assertRaises(ValidationError):
            self.tracker.create(application)
        with self.assertRaises(ValidationError):
            self.tracker.update(Application("missing", "Acme", "Engineer"))

    def test_followups_are_deterministic(self):
        due = validate_application(application_data())
        not_due = validate_application(application_data(application_id="app-2", follow_up_date="2026-10-01"))
        followups = FollowUpService()
        self.assertTrue(followups.is_due(due, on_date=date(2026, 9, 27)))
        self.assertFalse(followups.is_due(not_due, on_date=date(2026, 9, 27)))

    def test_message_uses_supplied_facts(self):
        message = FollowUpMessageGenerator().generate(validate_application(application_data()))
        self.assertIn("Engineer", message)
        self.assertIn("Acme", message)

    def test_analytics(self):
        applications = tuple(validate_application(application_data(application_id=f"app-{index}", status=status)) for index, status in enumerate(("applied", "interview", "offer", "rejected"), 1))
        metrics = ApplicationAnalytics().summarize(applications)
        self.assertEqual(metrics.total_applications, 4)
        self.assertEqual(metrics.interviews, 1)
        self.assertEqual(metrics.offers, 1)
        self.assertEqual(metrics.rejections, 1)

    def test_service_metrics(self):
        self.service.create(application_data())
        self.assertEqual(self.service.metrics().total_applications, 1)


if __name__ == "__main__":
    unittest.main()
