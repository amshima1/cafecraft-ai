"""Job description analysis orchestration."""

from __future__ import annotations

from ai.engine import AIEngine
from ai.parser import parse_ai_response
from ai.prompts.job import build_job_analysis_prompt
from core.validators import validate_required_text

from .models import JobAnalysisResult
from .schemas import validate_job_analysis


class JobAnalyzer:
    def __init__(self, engine: AIEngine) -> None:
        self._engine = engine

    def analyze_job(self, job_description: str) -> JobAnalysisResult:
        description = validate_required_text(job_description, "job_description")
        response = self._engine.process_prompt(build_job_analysis_prompt(description))
        return validate_job_analysis(parse_ai_response(response))


def analyze_job(job_description: str, engine: AIEngine) -> JobAnalysisResult:
    """Analyze a job using an injected AI engine."""
    return JobAnalyzer(engine).analyze_job(job_description)
