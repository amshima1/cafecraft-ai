"""Application service for verified Career Profile data."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.exceptions import ValidationError
from core.validators import validate_required_text

from .models import CareerProfile
from .repository import CareerProfileRepository
from .schemas import validate_profile


class CareerProfileService:
    """Coordinate profile validation and repository operations."""

    def __init__(self, repository: CareerProfileRepository) -> None:
        self._repository = repository

    def create_profile(self, data: CareerProfile | Mapping[str, Any]) -> CareerProfile:
        return self._repository.save(validate_profile(data))

    def get_profile(self, profile_id: str) -> CareerProfile | None:
        return self._repository.get(validate_required_text(profile_id, "profile_id"))

    def update_profile(self, profile_id: str, data: CareerProfile | Mapping[str, Any]) -> CareerProfile:
        profile_id = validate_required_text(profile_id, "profile_id")
        if isinstance(data, CareerProfile):
            if data.profile_id != profile_id:
                raise ValidationError("profile_id cannot change during an update.")
            profile = data
        else:
            values = dict(data)
            values["profile_id"] = profile_id
            profile = validate_profile(values)
        return self._repository.update(profile)

    def delete_profile(self, profile_id: str) -> None:
        self._repository.delete(validate_required_text(profile_id, "profile_id"))
