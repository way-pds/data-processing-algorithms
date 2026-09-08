"""Filename metadata parsing.

Provides a single, robust parser for the conventional dataset naming scheme
used across the repository::

    <participant>_<category>_<device>_<extra1>_<extra2>_<date>

where fields are separated by underscores. The parser is tolerant of names
with fewer fields than the full scheme.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class FileNameInfo:
    """Structured metadata parsed from a file name."""

    participant: str | None = None
    category: str | None = None
    device: str | None = None
    extra_1: str | None = None
    extra_2: str | None = None
    date: str | None = None
    raw_parts: tuple[str, ...] = field(default_factory=tuple)

    @property
    def pattern_valid(self) -> bool:
        """Whether the name had enough underscore-separated fields."""
        return len(self.raw_parts) >= 3


def parse_filename(file: str | Path) -> FileNameInfo:
    """Parse a file name (stem only) into structured fields.

    Fields are read positionally from the underscore-separated stem, so short
    or unconventional names degrade gracefully to ``None`` instead of raising.

    Args:
        file: Path (or path-like) to inspect. Only the stem is parsed.

    Returns:
        A :class:`FileNameInfo` with the extracted fields.
    """
    path = Path(file)
    parts = path.stem.split("_")

    def get(index: int) -> str | None:
        if 0 <= index < len(parts):
            return parts[index] or None
        return None

    return FileNameInfo(
        participant=get(0),
        category=get(1),
        device=get(2),
        extra_1=get(3),
        extra_2=get(4),
        date=get(5),
        raw_parts=tuple(p.lower() for p in parts if p),
    )
