"""Builder that converts verified Career Profile data into Resume data."""

from __future__ import annotations

from dataclasses import asdict

from career_profile.models import CareerProfile
from core.exceptions import ValidationError

from .models import Resume, ResumeEntry, ResumeSection


class ResumeBuilder:
    """Convert verified Career Profile facts into a deterministic Resume."""

    def build_from_profile(self, profile: CareerProfile) -> Resume:
        if not isinstance(profile, CareerProfile):
            raise ValidationError("profile must be a CareerProfile instance.")

        sections = [
            ResumeSection(
                name="Summary",
                entries=(ResumeEntry(title="Professional Summary", content=profile.professional_summary),),
            ) if profile.professional_summary else None,
            ResumeSection(
                name="Experience",
                entries=tuple(
                    ResumeEntry(
                        title=item.job_title,
                        content=item.employer,
                        details=tuple(filter(None, [item.description])),
                        dates=(item.start_date.isoformat(), item.end_date.isoformat() if item.end_date else "Present"),
                        metadata=tuple(item.skills),
                    )
                    for item in profile.work_experience
                ),
            ),
            ResumeSection(
                name="Education",
                entries=tuple(
                    ResumeEntry(
                        title=item.degree,
                        content=item.institution,
                        details=tuple(filter(None, [item.field_of_study, item.details])),
                        dates=(item.start_date.isoformat() if item.start_date else "", item.end_date.isoformat() if item.end_date else ""),
                    )
                    for item in profile.education
                ),
            ),
            ResumeSection(
                name="Skills",
                entries=(ResumeEntry(title="Technical Skills", content=", ".join(profile.skills)),) if profile.skills else (),
            ),
            ResumeSection(
                name="Certifications",
                entries=tuple(
                    ResumeEntry(
                        title=item.name,
                        content=item.issuer,
                        dates=(item.issue_date.isoformat() if item.issue_date else "", item.expiration_date.isoformat() if item.expiration_date else ""),
                    )
                    for item in profile.certifications
                ),
            ),
            ResumeSection(
                name="Projects",
                entries=tuple(
                    ResumeEntry(
                        title=item.name,
                        content=item.description,
                        metadata=tuple(item.technologies),
                    )
                    for item in profile.projects
                ),
            ),
            ResumeSection(
                name="Achievements",
                entries=tuple(
                    ResumeEntry(
                        title=item.title,
                        content=item.description,
                        dates=(item.date.isoformat(),) if item.date else (),
                    )
                    for item in profile.achievements
                ),
            ),
        ]

        # Remove empty optional sections while preserving order.
        valid_sections = tuple(section for section in sections if section and section.entries)
        return Resume(
            resume_id=f"resume-{profile.profile_id}",
            full_name=profile.full_name,
            email=profile.email,
            summary=profile.professional_summary,
            skills=profile.skills,
            sections=valid_sections,
        )
