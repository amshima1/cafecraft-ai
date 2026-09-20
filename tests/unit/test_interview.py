"""Unit tests for Interview Intelligence foundation."""

import unittest

from core.exceptions import ValidationError
from interview_intelligence import (
    AnswerAnalyzer,
    InterviewIntelligenceService,
    InterviewQuestion,
    InterviewQuestionGenerator,
    PracticeSession,
)
from interview_intelligence.schemas import validate_question, validate_session


class InterviewTests(unittest.TestCase):
    def setUp(self):
        self.question = InterviewQuestion("q1", "Tell me about Python.", "skill", "medium", "job", ("example",))

    def test_valid_question_and_immutable_models(self):
        question = validate_question({"question_id": "q1", "question": "Tell me about Python.", "category": "skill", "difficulty": "medium", "source": "job", "evidence_needed": ["example"]})
        with self.assertRaises((AttributeError, TypeError)):
            question.question = "Changed"

    def test_invalid_question_input(self):
        with self.assertRaises(ValidationError):
            validate_question({"question_id": "", "question": "Q", "category": "skill", "difficulty": "medium", "source": "job"})
        with self.assertRaises(ValidationError):
            validate_question({"question_id": "q", "question": "Q", "category": "skill", "difficulty": "medium", "source": "job", "evidence_needed": "example"})

    def test_question_generation_and_empty_requirements(self):
        generator = InterviewQuestionGenerator()
        questions = generator.generate({"required_skills": ["Python"], "responsibilities": ["testing"]})
        self.assertEqual(len(questions), 2)
        self.assertTrue(all(item.source == "generated_practice_from_job_requirement" for item in questions))
        self.assertEqual(generator.generate({}), ())

    def test_answer_analysis(self):
        analysis = AnswerAnalyzer().analyze(self.question, "I implemented a service and reduced processing time by 20%.")
        self.assertTrue(analysis.strengths)
        self.assertFalse(analysis.missing_evidence)

    def test_empty_answer(self):
        analysis = AnswerAnalyzer().analyze(self.question, "")
        self.assertIn("No answer was supplied.", analysis.missing_evidence)

    def test_unsupported_claim_boundary(self):
        analysis = AnswerAnalyzer().analyze(self.question, "I used Python.", supplied_context=("verified employer",))
        self.assertEqual(analysis.unsupported_claims, ("verified employer",))

    def test_practice_lifecycle_and_retrieval(self):
        service = InterviewIntelligenceService()
        created = service.create_session({"session_id": "s1", "question_id": "q1"})
        self.assertFalse(created.completed)
        analysis = service.analyze_answer(self.question, "I built a tool and achieved 10% improvement.")
        recorded = service.record_answer("s1", "I built a tool and achieved 10% improvement.", analysis)
        self.assertIs(service.get_session("s1"), recorded)
        completed = service.complete_session("s1")
        self.assertTrue(completed.completed)

    def test_invalid_session_data(self):
        with self.assertRaises(ValidationError):
            validate_session({"session_id": "", "question_id": "q1"})
        with self.assertRaises(ValidationError):
            validate_session({"session_id": "s1", "question_id": "q1", "completed": "yes"})

    def test_service_store_separation(self):
        class Store:
            def __init__(self): self.sessions = {}
            def create(self, session): self.sessions[session.session_id] = session; return session
            def get(self, session_id): return self.sessions.get(session_id)
            def update(self, session): self.sessions[session.session_id] = session; return session
        service = InterviewIntelligenceService(Store())
        self.assertEqual(service.create_session({"session_id": "s", "question_id": "q"}).session_id, "s")


if __name__ == "__main__":
    unittest.main()
