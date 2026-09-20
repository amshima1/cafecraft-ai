"""Persistence-neutral user data export."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any


class DataExporter:
    """Create an independent, deterministic copy of supplied user data."""

    def export(self, data: Any) -> Any:
        """Return supplied data without mutating or augmenting it."""
        return deepcopy(data)
