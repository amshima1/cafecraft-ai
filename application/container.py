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
        self._career_profiles = (
            career_profiles
            if career_profiles is not None
            else CareerProfileService(InMemoryCareerProfileRepository())
        )
        self._resumes = resumes if resumes is not None else ResumeService()
        self._jobs = jobs if jobs is not None else None
        self._applications = (
            applications
            if applications is not None
            else ApplicationWorkspaceService()
        )
        self._interviews = (
            interviews
            if interviews is not None
            else InterviewIntelligenceService()
        )
        self._truth = truth if truth is not None else TruthLayerService()
        self._privacy = privacy if privacy is not None else PrivacyService()
        self._documents = documents if documents is not None else DocumentService()
        self._storage = (
            storage if storage is not None else StorageService[object]()
        )

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
