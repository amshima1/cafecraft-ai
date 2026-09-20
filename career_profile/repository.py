"""Persistence abstractions and an in-memory repository for Career Profiles."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from core.exceptions import ValidationError

from .models import CareerProfile

_Profile = TypeVar("_Profile", bound=CareerProfile)


class CareerProfileRepository(ABC):
    """Storage boundary used by the Career Profile service."""

    @abstractmethod
    def save(self, profile: CareerProfile) -> CareerProfile:
        raise NotImplementedError

    @abstractmethod
    def get(self, profile_id: str) -> CareerProfile | None:
        raise NotImplementedError

    @abstractmethod
    def update(self, profile: CareerProfile) -> CareerProfile:
        raise NotImplementedError

    @abstractmethod
    def delete(self, profile_id: str) -> None:
        raise NotImplementedError


class InMemoryCareerProfileRepository(CareerProfileRepository):
    """Deterministic repository useful for local use and unit tests."""

    def __init__(self) -> None:
        self._profiles: dict[str, CareerProfile] = {}

    def save(self, profile: CareerProfile) -> CareerProfile:
        if profile.profile_id in self._profiles:
            raise ValidationError("A career profile with this profile_id already exists.")
        self._profiles[profile.profile_id] = profile
        return profile

    def get(self, profile_id: str) -> CareerProfile | None:
        return self._profiles.get(profile_id)

    def update(self, profile: CareerProfile) -> CareerProfile:
        if profile.profile_id not in self._profiles:
            raise ValidationError("Career profile does not exist.")
        self._profiles[profile.profile_id] = profile
        return profile

    def delete(self, profile_id: str) -> None:
        self._profiles.pop(profile_id, None)
