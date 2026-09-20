"""Application-level facade for Job Intelligence operations."""

from __future__ import annotations

from ai.engine import AIEngine

from .analyzer import JobAnalyzer
from .ats import ATSAnalyzer
from .gap_analyzer import GapAnalyzer
from .matcher import CandidateMatcher
from .models import ATSAnalysisResult, JobAnalysisResult, JobGapAnalysisResult, JobMatchingResult


class JobIntelligenceService:
    """Coordinate Job Intelligence components around one injected AI engine."""

    def __init__(self, engine: AIEngine) -> None:
        self._analyzer = JobAnalyzer(engine)
        self._matcher = CandidateMatcher(engine)
        self._ats = ATSAnalyzer(engine)
        self._gap_analyzer = GapAnalyzer(engine)

    def analyze_job(self, job_description: str) -> JobAnalysisResult:
        return self._analyzer.analyze_job(job_description)

    def match_candidate(self, job_description: str, candidate_profile: str) -> JobMatchingResult:
        return self._matcher.match_candidate(job_description, candidate_profile)

    def analyze_ats(self, job_description: str, resume_content: str) -> ATSAnalysisResult:
        return self._ats.analyze_ats(job_description, resume_content)

    def analyze_gaps(self, job_description: str, candidate_profile: str) -> JobGapAnalysisResult:
        return self._gap_analyzer.analyze_gaps(job_description, candidate_profile)
