"""Job-to-candidate gap analysis orchestration."""

from __future__ import annotations

from ai.engine import AIEngine
from ai.parser import parse_ai_response
from ai.prompts.job import build_job_gap_analysis_prompt
from core.validators import validate_required_text

from .models import JobGapAnalysisResult
from .schemas import validate_gap_analysis


class GapAnalyzer:
    def __init__(self, engine: AIEngine) -> None:
        self._engine = engine

    def analyze_gaps(self, job_description: str, candidate_profile: str) -> JobGapAnalysisResult:
        job = validate_required_text(job_description, "job_description")
        candidate = validate_required_text(candidate_profile, "candidate_profile")
        response = self._engine.process_prompt(build_job_gap_analysis_prompt(job, candidate))
        return validate_gap_analysis(parse_ai_response(response))


def analyze_gaps(job_description: str, candidate_profile: str, engine: AIEngine) -> JobGapAnalysisResult:
    """Identify confirmed gaps separately from missing information."""
    return GapAnalyzer(engine).analyze_gaps(job_description, candidate_profile)
