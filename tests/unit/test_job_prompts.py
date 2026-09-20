"""Unit tests for the job prompt builders."""

import unittest

from ai.prompts.job import (
    build_ats_analysis_prompt,
    build_job_analysis_prompt,
    build_job_gap_analysis_prompt,
    build_job_matching_prompt,
)
from core.exceptions import ValidationError


class JobPromptBuilderTests(unittest.TestCase):
    """Verify the public behavior of the job prompt builders."""

    def assert_truth_layer_instructions(self, prompt: str) -> None:
        """The prompt must require evidence-based, non-invented facts."""
        self.assertIn("Truth Layer", prompt)
        self.assertIn("Never invent", prompt)
        self.assertIn("must not fill it with an assumption", prompt)

    def assert_json_output_instructions(self, prompt: str) -> None:
        """Prompts must require valid JSON output with a fixed schema."""
        self.assertIn("Return one valid JSON object", prompt)
        self.assertIn("top-level structure exactly", prompt)

    def test_build_job_analysis_prompt_returns_nonempty_prompt(self) -> None:
        """The job analysis builder returns a populated prompt."""
        job_description = "Senior Python engineer responsible for building data pipelines."

        prompt = build_job_analysis_prompt(job_description)

        self.assertIsInstance(prompt, str)
        self.assertTrue(prompt.strip())
        self.assertIn(job_description, prompt)
        self.assert_truth_layer_instructions(prompt)
        self.assert_json_output_instructions(prompt)

    def test_build_job_matching_prompt_returns_nonempty_prompt(self) -> None:
        """The matching prompt includes the supplied job and candidate text."""
        job_description = "Requires Python, SQL, and cloud experience."
        candidate_profile = "Candidate has Python, SQL, and 5 years of backend work."

        prompt = build_job_matching_prompt(job_description, candidate_profile)

        self.assertIsInstance(prompt, str)
        self.assertTrue(prompt.strip())
        self.assertIn(job_description, prompt)
        self.assertIn(candidate_profile, prompt)
        self.assert_truth_layer_instructions(prompt)
        self.assert_json_output_instructions(prompt)

    def test_build_ats_analysis_prompt_returns_nonempty_prompt(self) -> None:
        """The ATS builder returns a populated prompt."""
        job_description = "Looking for machine learning engineer with Python and AWS."
        resume_content = "Built ML models in Python and deployed on AWS."

        prompt = build_ats_analysis_prompt(job_description, resume_content)

        self.assertIsInstance(prompt, str)
        self.assertTrue(prompt.strip())
        self.assertIn(job_description, prompt)
        self.assertIn(resume_content, prompt)
        self.assert_truth_layer_instructions(prompt)
        self.assert_json_output_instructions(prompt)

    def test_build_job_gap_analysis_prompt_returns_nonempty_prompt(self) -> None:
        """The gap-analysis prompt includes the provided context."""
        job_description = "Requires a leadership role with stakeholder communication."
        candidate_profile = "Has technical work but no leadership examples listed."

        prompt = build_job_gap_analysis_prompt(job_description, candidate_profile)

        self.assertIsInstance(prompt, str)
        self.assertTrue(prompt.strip())
        self.assertIn(job_description, prompt)
        self.assertIn(candidate_profile, prompt)
        self.assert_truth_layer_instructions(prompt)
        self.assert_json_output_instructions(prompt)

    def test_job_analysis_prompt_validates_required_input(self) -> None:
        """job_description must be non-empty text."""
        invalid_values = ["", "   ", "\n\t", None, 123, [], {}]

        for value in invalid_values:
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValidationError):
                    build_job_analysis_prompt(value)

    def test_job_matching_prompt_validates_required_inputs(self) -> None:
        """Both builder arguments must be non-empty text."""
        valid_candidate = "Candidate has Python and SQL experience."
        valid_job = "Needs Python and SQL."

        for value in ["", "   ", "\n\t", None, 123, [], {}]:
            with self.subTest(job_description=repr(value)):
                with self.assertRaises(ValidationError):
                    build_job_matching_prompt(value, valid_candidate)

        for value in ["", "   ", "\n\t", None, 123, [], {}]:
            with self.subTest(candidate_profile=repr(value)):
                with self.assertRaises(ValidationError):
                    build_job_matching_prompt(valid_job, value)

    def test_ats_analysis_prompt_validates_required_inputs(self) -> None:
        """job_description and resume_content must be non-empty text."""
        valid_resume = "Customer-facing backend engineer with Python."
        valid_job = "Needs Python and AWS."

        for value in ["", "   ", "\n\t", None, 123, [], {}]:
            with self.subTest(job_description=repr(value)):
                with self.assertRaises(ValidationError):
                    build_ats_analysis_prompt(value, valid_resume)

        for value in ["", "   ", "\n\t", None, 123, [], {}]:
            with self.subTest(resume_content=repr(value)):
                with self.assertRaises(ValidationError):
                    build_ats_analysis_prompt(valid_job, value)

    def test_job_gap_analysis_prompt_validates_required_inputs(self) -> None:
        """Both inputs must be non-empty strings."""
        valid_candidate = "Strong technical skills but limited leadership examples."
        valid_job = "Requires leadership and product thinking."

        for value in ["", "   ", "\n\t", None, 123, [], {}]:
            with self.subTest(job_description=repr(value)):
                with self.assertRaises(ValidationError):
                    build_job_gap_analysis_prompt(value, valid_candidate)

        for value in ["", "   ", "\n\t", None, 123, [], {}]:
            with self.subTest(candidate_profile=repr(value)):
                with self.assertRaises(ValidationError):
                    build_job_gap_analysis_prompt(valid_job, value)

    def test_job_analysis_prompt_mentions_requirement_extraction(self) -> None:
        """The prompt calls for extracting job requirements."""
        prompt = build_job_analysis_prompt("Data engineer role with Python and ETL experience.")

        self.assertIn("Extract and organize", prompt)
        self.assertIn("relevant requirements", prompt)

    def test_job_matching_prompt_distinguishes_matches_missing_and_uncertain(self) -> None:
        """Matching distinguishes matches, missing requirements, and uncertainty."""
        prompt = build_job_matching_prompt(
            "Requires Python, SQL, and stakeholder communication.",
            "Has Python, SQL, but no communication examples listed.",
        )

        self.assertIn("matches", prompt.lower())
        self.assertIn("missing_requirements", prompt.lower())
        self.assertIn("uncertain_requirements", prompt.lower())
        self.assertIn("supported by direct evidence", prompt)
        self.assertIn("not supported by the profile", prompt)

    def test_ats_analysis_prompt_rejects_exact_score_claims(self) -> None:
        """ATS analysis avoids exact score claims."""
        prompt = build_ats_analysis_prompt(
            "Needs Python and data engineering experience.",
            "Built ETL pipelines in Python.",
        )

        self.assertIn("exact ats score", prompt.lower())
        self.assertIn("No exact ATS score is predicted.", prompt)
        self.assertIn("qualitative analysis only", prompt.lower())

    def test_gap_analysis_prompt_distinguishes_confirmed_gaps_from_missing_information(self) -> None:
        """Gap analysis separates confirmed gaps from missing info."""
        prompt = build_job_gap_analysis_prompt(
            "Requires cloud certification and leadership experience.",
            "Has cloud work but no certification or leadership examples.",
        )
        normalized_prompt = " ".join(prompt.split())

        self.assertIn("confirmed gaps", prompt.lower())
        self.assertIn("missing information", prompt.lower())
        self.assertIn(
            "explicitly shows the candidate does not meet a requirement",
            normalized_prompt,
        )


if __name__ == "__main__":
    unittest.main()
