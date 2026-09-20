"""Qualitative ATS alignment orchestration."""

from __future__ import annotations

from ai.engine import AIEngine
from ai.parser import parse_ai_response
from ai.prompts.job import build_ats_analysis_prompt
from core.validators import validate_required_text

from .models import ATSAnalysisResult
from .schemas import validate_ats_analysis


class ATSAnalyzer:
    def __init__(self, engine: AIEngine) -> None:
        self._engine = engine

    def analyze_ats(self, job_description: str, resume_content: str) -> ATSAnalysisResult:
        job = validate_required_text(job_description, "job_description")
        resume = validate_required_text(resume_content, "resume_content")
        response = self._engine.process_prompt(build_ats_analysis_prompt(job, resume))
        return validate_ats_analysis(parse_ai_response(response))


def analyze_ats(job_description: str, resume_content: str, engine: AIEngine) -> ATSAnalysisResult:
    """Perform qualitative ATS alignment analysis without an exact score."""
    return ATSAnalyzer(engine).analyze_ats(job_description, resume_content)
