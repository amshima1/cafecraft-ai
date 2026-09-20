"""Unit tests for the job intelligence package."""

import json
import unittest

from core.exceptions import ValidationError
from job_intelligence import JobIntelligenceService
from job_intelligence.analyzer import JobAnalyzer
from job_intelligence.ats import ATSAnalyzer
from job_intelligence.gap_analyzer import GapAnalyzer
from job_intelligence.matcher import CandidateMatcher
from job_intelligence.models import (
    ATSAnalysisResult,
    JobAnalysisResult,
    JobGapAnalysisResult,
    JobMatchingResult,
)
from job_intelligence.schemas import (
    validate_ats_analysis,
    validate_gap_analysis,
    validate_job_analysis,
    validate_job_matching,
)


class _DummyEngine:
    """Return a fixed JSON response for any prompt."""

    def __init__(self, payload):
        self.payload = payload

    def process_prompt(self, prompt):
        return json.dumps(self.payload)


class JobIntelligenceSchemaTests(unittest.TestCase):
    """Validate schema conversion and required fields."""

    def test_validate_job_analysis_accepts_valid_payload(self):
        payload = {
            "responsibilities": ["build pipelines"],
            "required_skills": ["Python"],
            "preferred_skills": ["SQL"],
            "qualifications": ["BS degree"],
            "experience_requirements": ["3+ years"],
            "keywords": ["ETL"],
            "other_requirements": ["remote"],
            "missing_or_ambiguous_information": ["licensing details"],
        }

        result = validate_job_analysis(payload)

        self.assertIsInstance(result, JobAnalysisResult)
        self.assertEqual(result.required_skills, ["Python"])

    def test_validate_job_matching_accepts_valid_payload(self):
        payload = {
            "matches": ["Python"],
            "missing_requirements": ["leadership"],
            "uncertain_requirements": ["cloud"],
            "evidence_needed": ["deployment examples"],
            "candidate_strengths": ["backend"],
            "notes": ["candidate evidence is direct"],
        }

        result = validate_job_matching(payload)

        self.assertIsInstance(result, JobMatchingResult)
        self.assertEqual(result.matches, ["Python"])

    def test_validate_ats_analysis_accepts_valid_payload(self):
        payload = {
            "relevant_keywords": ["Python", "AWS"],
            "matched_keywords": ["Python"],
            "unrepresented_keywords": ["AWS"],
            "alignment_issues": ["missing examples"],
            "supported_improvements": ["Add AWS projects"],
            "verification_needed": ["confirm certifications"],
            "ats_score_statement": "No exact ATS score is predicted.",
        }

        result = validate_ats_analysis(payload)

        self.assertIsInstance(result, ATSAnalysisResult)
        self.assertEqual(result.ats_score_statement, "No exact ATS score is predicted.")

    def test_validate_gap_analysis_accepts_valid_payload(self):
        payload = {
            "confirmed_gaps": ["leadership"],
            "missing_information": ["certification"],
            "supported_requirements": ["Python"],
            "evidence_needed": ["proof of AWS"],
            "notes": ["candidate has direct backend evidence"],
        }

        result = validate_gap_analysis(payload)

        self.assertIsInstance(result, JobGapAnalysisResult)
        self.assertEqual(result.confirmed_gaps, ["leadership"])

    def test_validate_ats_analysis_rejects_invalid_score_statement(self):
        payload = {
            "relevant_keywords": [],
            "matched_keywords": [],
            "unrepresented_keywords": [],
            "alignment_issues": [],
            "supported_improvements": [],
            "verification_needed": [],
            "ats_score_statement": "82% ATS match",
        }

        with self.assertRaises(ValidationError):
            validate_ats_analysis(payload)

    def test_validate_functions_reject_non_object_payloads(self):
        for validator in (
            validate_job_analysis,
            validate_job_matching,
            validate_ats_analysis,
            validate_gap_analysis,
        ):
            with self.subTest(validator=validator.__name__):
                with self.assertRaises(ValidationError):
                    validator("not a JSON object")


class JobIntelligenceAnalyzerTests(unittest.TestCase):
    """Verify analyzer flows use AIEngine and validate structured outputs."""

    def test_job_analyzer_uses_injected_engine(self):
        payload = {
            "responsibilities": ["build pipelines"],
            "required_skills": ["Python"],
            "preferred_skills": ["SQL"],
            "qualifications": ["B.S."],
            "experience_requirements": ["three years"],
            "keywords": ["ETL"],
            "other_requirements": ["remote"],
            "missing_or_ambiguous_information": [],
        }
        engine = _DummyEngine(payload)

        result = JobAnalyzer(engine).analyze_job("Python data engineer")

        self.assertIsInstance(result, JobAnalysisResult)
        self.assertIn("Python", result.required_skills)

    def test_matcher_uses_injected_engine(self):
        payload = {
            "matches": ["Python"],
            "missing_requirements": ["leadership"],
            "uncertain_requirements": [],
            "evidence_needed": ["stakeholder examples"],
            "candidate_strengths": ["backend"],
            "notes": ["fit is moderate"],
        }
        engine = _DummyEngine(payload)

        result = CandidateMatcher(engine).match_candidate("Python role", "Python backend experience")

        self.assertIsInstance(result, JobMatchingResult)
        self.assertIn("Python", result.matches)

    def test_ats_analyzer_uses_injected_engine(self):
        payload = {
            "relevant_keywords": ["Python"],
            "matched_keywords": ["Python"],
            "unrepresented_keywords": [],
            "alignment_issues": [],
            "supported_improvements": [],
            "verification_needed": [],
            "ats_score_statement": "No exact ATS score is predicted.",
        }
        engine = _DummyEngine(payload)

        result = ATSAnalyzer(engine).analyze_ats("Python role", "Python and SQL projects")

        self.assertIsInstance(result, ATSAnalysisResult)
        self.assertEqual(result.ats_score_statement, "No exact ATS score is predicted.")

    def test_gap_analyzer_uses_injected_engine(self):
        payload = {
            "confirmed_gaps": ["leadership"],
            "missing_information": ["certification"],
            "supported_requirements": ["Python"],
            "evidence_needed": ["leadership examples"],
            "notes": ["role requires leadership"],
        }
        engine = _DummyEngine(payload)

        result = GapAnalyzer(engine).analyze_gaps("Python leadership role", "Python developer")

        self.assertIsInstance(result, JobGapAnalysisResult)
        self.assertIn("leadership", result.confirmed_gaps)

    def test_invalid_inputs_raise_validation_error(self):
        engine = _DummyEngine({})

        with self.assertRaises(ValidationError):
            JobAnalyzer(engine).analyze_job("")

        with self.assertRaises(ValidationError):
            CandidateMatcher(engine).match_candidate("Python role", "")

        with self.assertRaises(ValidationError):
            ATSAnalyzer(engine).analyze_ats("Python role", None)

        with self.assertRaises(ValidationError):
            GapAnalyzer(engine).analyze_gaps(None, "Python developer")


class JobIntelligenceServiceTests(unittest.TestCase):
    """Verify the service delegates to the appropriate components."""

    def test_service_delegates_to_component_methods(self):
        engine = _DummyEngine({
            "responsibilities": ["build pipelines"],
            "required_skills": ["Python"],
            "preferred_skills": ["SQL"],
            "qualifications": ["B.S."],
            "experience_requirements": ["3 years"],
            "keywords": ["ETL"],
            "other_requirements": [],
            "missing_or_ambiguous_information": [],
            "matches": ["Python"],
            "missing_requirements": [],
            "uncertain_requirements": [],
            "evidence_needed": [],
            "candidate_strengths": ["Python"],
            "notes": ["Good fit"],
            "relevant_keywords": ["Python"],
            "matched_keywords": ["Python"],
            "unrepresented_keywords": [],
            "alignment_issues": [],
            "supported_improvements": [],
            "verification_needed": [],
            "ats_score_statement": "No exact ATS score is predicted.",
            "confirmed_gaps": [],
            "missing_information": [],
            "supported_requirements": ["Python"],
            "evidence_needed": [],
            "notes": ["Good fit"],
        })
        service = JobIntelligenceService(engine)

        self.assertIsInstance(service.analyze_job("Python role"), JobAnalysisResult)
        self.assertIsInstance(service.match_candidate("Python role", "Python developer"), JobMatchingResult)
        self.assertIsInstance(service.analyze_ats("Python role", "Python developer"), ATSAnalysisResult)
        self.assertIsInstance(service.analyze_gaps("Python role", "Python developer"), JobGapAnalysisResult)


if __name__ == "__main__":
    unittest.main()
