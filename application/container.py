"""Dependency-injected application service composition."""

from __future__ import annotations

from typing import TYPE_CHECKING

from application_workspace import ApplicationWorkspaceService
from career_profile import CareerProfileService, InMemoryCareerProfileRepository
from documents import DocumentService
from interview_intelligence import InterviewIntelligenceService
from privacy import PrivacyService
from resume_intelligence import ResumeService
from storage import StorageService
from truth_layer import TruthLayerService

if TYPE_CHECKING:
    from job_intelligence import JobIntelligenceService


class ApplicationContainer:
    """Own isolated feature-service instances for one application scope."""

    def __init__(
        self,
        *,
        career_profiles: CareerProfileService | None = None,
        resumes: ResumeService | None = None,
        jobs: JobIntelligenceService | None = None,
        applications: ApplicationWorkspaceService | None = None,
        interviews: InterviewIntelligenceService | None = None,
        truth: TruthLayerService | None = None,
        privacy: PrivacyService | None = None,
        documents: DocumentService | None = None,
        storage: StorageService[object] | None = None,
    ) -> None:
        self._career_profiles = career_profiles or CareerProfileService(
            InMemoryCareerProfileRepository()
        )
        self._resumes = resumes or ResumeService()
        self._jobs = jobs
        self._applications = applications or ApplicationWorkspaceService()
        self._interviews = interviews or InterviewIntelligenceService()
        self._truth = truth or TruthLayerService()
        self._privacy = privacy or PrivacyService()
        self._documents = documents or DocumentService()
        self._storage = storage or StorageService[object]()

    @property
    def career_profiles(self) -> CareerProfileService:
        """Return the configured Career Profile service."""
        return self._career_profiles

    @property
    def resumes(self) -> ResumeService:
        """Return the configured Resume Intelligence service."""
        return self._resumes

    @property
    def jobs(self) -> JobIntelligenceService | None:
        """Return the explicitly configured Job Intelligence service, if any."""
        return self._jobs

    @property
    def applications(self) -> ApplicationWorkspaceService:
        """Return the configured Application Workspace service."""
        return self._applications

    @property
    def interviews(self) -> InterviewIntelligenceService:
        """Return the configured Interview Intelligence service."""
        return self._interviews

    @property
    def truth(self) -> TruthLayerService:
        """Return the configured Truth Layer service."""
        return self._truth

    @property
    def privacy(self) -> PrivacyService:
        """Return the configured Privacy service."""
        return self._privacy

    @property
    def documents(self) -> DocumentService:
        """Return the configured Documents service."""
        return self._documents

    @property
    def storage(self) -> StorageService[object]:
        """Return the configured Storage service."""
        return self._storage
