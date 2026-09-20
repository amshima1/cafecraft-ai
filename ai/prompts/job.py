"""Prompt builders for job intelligence tasks.

This module is deliberately limited to constructing prompts for AI-assisted job
analysis. It does not call external APIs, access a database, parse model output,
or perform business logic.
"""

from __future__ import annotations

from core.exceptions import ValidationError

__all__ = [
    "build_job_analysis_prompt",
    "build_job_matching_prompt",
    "build_ats_analysis_prompt",
    "build_job_gap_analysis_prompt",
]


def _require_non_empty_text(value: str, field_name: str) -> str:
    """Return trimmed text, or raise ValidationError when it is empty."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} must be non-empty text.")
    return value.strip()


def _truth_layer_instructions() -> str:
    """Return the non-negotiable factual-integrity instructions."""
    return """Truth Layer (non-negotiable):
- Use only information explicitly present in the supplied job description or
  candidate material.
- Never invent, assume, or guess qualifications, employers, job titles, dates,
  skills, achievements, metrics, certifications, education, responsibilities,
  or any other candidate facts.
- Preserve the meaning of candidate-provided information; do not strengthen,
  reinterpret, or contradict it.
- You may identify missing information, ambiguity, or unsupported claims, but
  must label it clearly and must not fill it with an assumption.
- Treat the job description as requirements to analyze, not as evidence that
  the candidate has those requirements.
"""


def _json_instructions(schema: str) -> str:
    """Return shared instructions for deterministic structured output."""
    return f"""Output requirements:
- Return one valid JSON object and no markdown, commentary, or code fences.
- Use the following top-level structure exactly; use arrays for lists and null
  or an empty array when the source does not provide information:
{schema}
- Keep every conclusion traceable to the supplied text. Do not add unsupported
  candidate facts.
"""


def build_job_analysis_prompt(job_description: str) -> str:
    """Build a prompt for extracting structured requirements from a job posting."""
    job_content = _require_non_empty_text(job_description, "job_description")

    prompt = f"""You are analyzing a job description for a candidate-support workflow.

{_truth_layer_instructions()}

Task:
Extract and organize the job's stated responsibilities, required skills,
preferred skills, qualifications, experience requirements, keywords, and other
relevant requirements. Distinguish required items from preferred items and
record qualifications only when the job description states them.

Job description:
{job_content}

{_json_instructions('''{{
  "responsibilities": [],
  "required_skills": [],
  "preferred_skills": [],
  "qualifications": [],
  "experience_requirements": [],
  "keywords": [],
  "other_requirements": [],
  "missing_or_ambiguous_information": []
}}''')}
"""
    return prompt.strip()


def build_job_matching_prompt(job_description: str, candidate_profile: str) -> str:
    """Build a prompt for comparing a candidate profile with a job description."""
    job_content = _require_non_empty_text(job_description, "job_description")
    candidate_content = _require_non_empty_text(candidate_profile, "candidate_profile")

    prompt = f"""You are comparing a candidate profile with a target job description.

{_truth_layer_instructions()}

Task:
Compare the candidate's explicitly stated background with the job requirements.
Identify requirements that are supported by direct evidence, requirements that
are not supported by the profile, and evidence that would be needed to assess
an uncertain requirement. Do not treat a lack of evidence as proof that the
candidate lacks the requirement.

Job description:
{job_content}

Candidate profile:
{candidate_content}

{_json_instructions('''{{
  "matches": [],
  "missing_requirements": [],
  "uncertain_requirements": [],
  "evidence_needed": [],
  "candidate_strengths": [],
  "notes": []
}}''')}
For each comparison item, include the relevant job requirement, the candidate
evidence when present, and a concise explanation. Label a requirement as a
confirmed gap only when the candidate profile explicitly contradicts or lacks a
required fact in a way that supports that conclusion; otherwise classify it as
unknown or missing information.
"""
    return prompt.strip()


def build_ats_analysis_prompt(job_description: str, resume_content: str) -> str:
    """Build a prompt for a cautious, evidence-based ATS alignment analysis."""
    job_content = _require_non_empty_text(job_description, "job_description")
    resume_text = _require_non_empty_text(resume_content, "resume_content")

    prompt = f"""You are analyzing potential resume alignment with a target job description.

{_truth_layer_instructions()}

Task:
Identify relevant keywords and phrases from the job description, show whether
and where they are explicitly represented in the resume, and explain potential
alignment or discoverability issues such as unclear wording, missing keywords,
or formatting that may reduce machine-readable clarity. This is a qualitative
analysis only. Do not provide an exact ATS score, claim to calculate one, or
predict an ATS decision. Do not recommend adding a keyword as though the
candidate possesses that skill; flag it for verification when the resume does
not support it.

Job description:
{job_content}

Resume:
{resume_text}

{_json_instructions('''{{
  "relevant_keywords": [],
  "matched_keywords": [],
  "unrepresented_keywords": [],
  "alignment_issues": [],
  "supported_improvements": [],
  "verification_needed": [],
  "ats_score_statement": "No exact ATS score is predicted."
}}''')}
"""
    return prompt.strip()


def build_job_gap_analysis_prompt(job_description: str, candidate_profile: str) -> str:
    """Build a prompt for distinguishing confirmed gaps from unknown information."""
    job_content = _require_non_empty_text(job_description, "job_description")
    candidate_content = _require_non_empty_text(candidate_profile, "candidate_profile")

    prompt = f"""You are identifying gaps between a job's stated requirements and a candidate profile.

{_truth_layer_instructions()}

Task:
Assess each relevant job requirement against the candidate profile. Distinguish
confirmed gaps, where the supplied profile explicitly shows the candidate does
not meet a requirement, from missing information, where the profile does not
provide enough evidence to assess it. Also identify requirements the profile
explicitly supports and the factual evidence needed to resolve unknowns.

Job description:
{job_content}

Candidate profile:
{candidate_content}

{_json_instructions('''{{
  "confirmed_gaps": [],
  "missing_information": [],
  "supported_requirements": [],
  "evidence_needed": [],
  "notes": []
}}''')}
For every item, reference the job requirement and cite or summarize only the
corresponding candidate evidence that is explicitly present. Never convert an
unknown into a confirmed gap and never infer a qualification, employer, title,
date, skill, achievement, metric, or other candidate fact.
"""
    return prompt.strip()
