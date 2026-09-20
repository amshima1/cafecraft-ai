"""Candidate-to-job matching orchestration."""

from __future__ import annotations

from ai.engine import AIEngine
from ai.parser import parse_ai_response
from ai.prompts.job import build_job_matching_prompt
from core.validators import validate_required_text

from .models import JobMatchingResult
from .schemas import validate_job_matching


class CandidateMatcher:
    def __init__(self, engine: AIEngine) -> None:
        self._engine = engine

    def match_candidate(self, job_description: str, candidate_profile: str) -> JobMatchingResult:
        job = validate_required_text(job_description, "job_description")
        candidate = validate_required_text(candidate_profile, "candidate_profile")
        response = self._engine.process_prompt(build_job_matching_prompt(job, candidate))
        return validate_job_matching(parse_ai_response(response))


def match_candidate(job_description: str, candidate_profile: str, engine: AIEngine) -> JobMatchingResult:
    """Compare a candidate profile with a job using an injected AI engine."""
    return CandidateMatcher(engine).match_candidate(job_description, candidate_profile)
