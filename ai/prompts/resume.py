"""Prompt builders for resume intelligence tasks.

This module is deliberately limited to creating prompts for AI-assisted resume
work. It does not call external APIs, parse model output, or perform any
business logic.
"""

from __future__ import annotations

__all__ = [
    "build_resume_content_improvement_prompt",
    "build_resume_bullet_rewrite_prompt",
    "build_resume_information_extraction_prompt",
    "build_resume_tailoring_prompt",
    "build_achievement_improvement_prompt",
]


def _require_non_empty_text(value: str, field_name: str) -> str:
    """Return trimmed text, or raise ValueError when the value is empty."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be non-empty text.")
    return value.strip()


def _truth_layer_instructions() -> str:
    """Return the non-negotiable truth layer used across resume prompt builders."""
    return """Truth Layer (non-negotiable):
- Do not invent, assume, or infer any facts.
- Do not fabricate employers, job titles, dates, locations, responsibilities,
  skills, technologies, certifications, degrees, qualifications, achievements,
  metrics, or other factual details.
- Use only information that is explicitly present in the source material.
- If a fact is missing, identify the missing information clearly instead of
  guessing or filling in gaps.
- Preserve the user's original meaning, factual claims, tone, and intent.
- When rewriting, improve clarity and phrasing only without changing the
  substance of what the user actually accomplished or stated.
- If the requested rewrite would require unsupported facts, say so and ask for
  the missing information rather than inventing it.
"""


def _optional_section(label: str, value: str | None) -> str:
    """Return a labeled section for optional prompt context."""
    if value is None:
        return ""
    clean_value = value.strip()
    if not clean_value:
        return ""
    return f"{label}:\n{clean_value}\n"


def build_resume_content_improvement_prompt(
    resume_text: str,
    objective: str = "Improve the resume for clarity, impact, and readability.",
    target_role: str | None = None,
    job_description: str | None = None,
) -> str:
    """Build a prompt for improving resume wording while preserving facts.

    Args:
        resume_text: The resume content to revise.
        objective: Optional guidance describing the desired improvement style.
        target_role: Optional role or title the resume should support.
        job_description: Optional target job description for relevance.

    Returns:
        A prompt string that instructs the AI to improve resume wording without
        inventing or changing the user's underlying facts.
    """
    resume_content = _require_non_empty_text(resume_text, "resume_text")
    objective_text = _require_non_empty_text(objective, "objective")

    prompt = f"""You are improving a resume. Your task is to make the content clearer, stronger, and easier to read while preserving the user's factual claims and original meaning.

{_truth_layer_instructions()}

Goal:
{objective_text}

{_optional_section('Target role', target_role)}
{_optional_section('Target job description', job_description)}

Source resume:
{resume_content}

Instructions:
1. Improve grammar, flow, readability, and emphasis.
2. Keep the original meaning and factual claims intact.
3. Do not rewrite or strengthen statements with unsupported details.
4. If any important information is missing, identify the missing information rather than guessing.
5. Return the improved resume text only, with no explanations unless a fact is missing and needs to be flagged.
"""
    return prompt.strip()


def build_resume_bullet_rewrite_prompt(
    bullet_text: str,
    context: str | None = None,
    target_role: str | None = None,
    job_description: str | None = None,
) -> str:
    """Build a prompt for rewriting a single resume bullet without fabricating facts.

    Args:
        bullet_text: The original bullet point to rewrite.
        context: Optional surrounding job, project, or experience context.
        target_role: Optional job or role this bullet should support.
        job_description: Optional job description to align the bullet with.

    Returns:
        A prompt string requiring factual preservation and clearer phrasing.
    """
    bullet_content = _require_non_empty_text(bullet_text, "bullet_text")

    prompt = f"""You are rewriting one resume bullet point to improve clarity and impact.

{_truth_layer_instructions()}

Original bullet:
{bullet_content}

{_optional_section('Context', context)}
{_optional_section('Target role', target_role)}
{_optional_section('Target job description', job_description)}

Instructions:
1. Rewrite the bullet for readability, phrasing, and emphasis.
2. Preserve the user's original meaning and all factual claims exactly.
3. Do not add skills, accomplishments, metrics, achievements, employers, job
   titles, or dates that are not explicitly present.
4. If the bullet cannot be improved without adding unsupported information,
   explain the missing information instead of guessing.
5. Return only the rewritten bullet point.
"""
    return prompt.strip()


def build_resume_information_extraction_prompt(
    resume_text: str,
    requested_fields: str | None = None,
    notes: str | None = None,
) -> str:
    """Build a prompt to extract factual information from a resume.

    Args:
        resume_text: Resume content to analyze.
        requested_fields: Optional list or description of fields to extract.
        notes: Optional context about how to format or prioritize extraction.

    Returns:
        A prompt instructing the model to extract explicitly stated facts only.
    """
    resume_content = _require_non_empty_text(resume_text, "resume_text")
    field_text = requested_fields or (
        "employment history, job titles, companies, dates, education, skills, "
        "certifications, awards, accomplishments, and measurable results"
    )

    prompt = f"""You are extracting information from a resume.

{_truth_layer_instructions()}

Extract only facts that are explicitly present in the resume.
Requested fields or categories:
{field_text}

{_optional_section('Notes', notes)}

Resume text:
{resume_content}

Instructions:
1. List only facts supported by the resume.
2. If a requested field is missing, state that it is missing rather than
   inventing it.
3. Do not create employers, job titles, dates, skills, qualifications,
   achievements, metrics, or other facts not stated in the source.
4. Preserve original wording when a fact is included, and clearly label any
   missing information.
5. Return the extracted information in a clear, structured format.
"""
    return prompt.strip()


def build_resume_tailoring_prompt(
    resume_text: str,
    job_description: str,
    target_role: str | None = None,
    tailoring_focus: str | None = None,
) -> str:
    """Build a prompt for tailoring a resume to a specific job description.

    Args:
        resume_text: The resume content to tailor.
        job_description: The target job posting or role requirements.
        target_role: Optional target job title.
        tailoring_focus: Optional emphasis or strategy to apply.

    Returns:
        A prompt string that tailors the resume by relevance while preserving
        factual integrity.
    """
    resume_content = _require_non_empty_text(resume_text, "resume_text")
    job_content = _require_non_empty_text(job_description, "job_description")

    prompt = f"""You are tailoring a resume to align with a specific job description.

{_truth_layer_instructions()}

{_optional_section('Target role', target_role)}
{_optional_section('Tailoring focus', tailoring_focus)}

Target job description:
{job_content}

Source resume:
{resume_content}

Instructions:
1. Reorder, emphasize, and rewrite the resume so the most relevant experience,
   skills, and accomplishments stand out for this role.
2. Preserve all original facts and the user's real experience.
3. Do not invent employers, job titles, dates, achievements, metrics,
   education, certifications, or skills.
4. If the resume does not contain enough evidence for a requirement, identify
   the missing information clearly rather than filling the gap with assumptions.
5. Return only the tailored resume content or the revised bullets if the user
   asked for a partial rewrite.
"""
    return prompt.strip()


def build_achievement_improvement_prompt(
    achievement_text: str,
    context: str | None = None,
    target_role: str | None = None,
    job_description: str | None = None,
) -> str:
    """Build a prompt for improving achievement language without inventing facts.

    Args:
        achievement_text: The achievement or bullet point to strengthen.
        context: Optional project or role context for the achievement.
        target_role: Optional target role.
        job_description: Optional target job description.

    Returns:
        A prompt string that improves wording while keeping claims grounded in the
        original material.
    """
    achievement_content = _require_non_empty_text(
        achievement_text, "achievement_text"
    )

    prompt = f"""You are improving a resume achievement or bullet point for stronger phrasing.

{_truth_layer_instructions()}

Original achievement:
{achievement_content}

{_optional_section('Context', context)}
{_optional_section('Target role', target_role)}
{_optional_section('Target job description', job_description)}

Instructions:
1. Improve the wording, specificity, and readability of the achievement.
2. Preserve the user's original meaning and all factual claims.
3. Do not invent new accomplishments, metrics, outcomes, employers, job titles,
   skills, or dates.
4. If a fact is missing, identify the missing information instead of adding
   unsupported claims.
5. Return only the improved achievement or bullet text.
"""
    return prompt.strip()
