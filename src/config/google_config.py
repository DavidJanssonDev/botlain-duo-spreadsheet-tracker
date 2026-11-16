from dataclasses import dataclass, field, fields
from typing import Any, Self

from ..errors.config import build, optional_table


@dataclass(frozen=True, slots=True, kw_only=True)
class SheetConfig:
    tab_matches_data: str = field(default="Matches Data")
    tab_players_data: str = field(default="Players Data")
    tab_events_data: str = field(default="Events Data")
    tab_bans_data: str = field(default="Bans Data")
    tab_duo_data: str = field(default="Duo Stats")

    def __post_init__(self) -> None:
        names = {f.name: getattr(self, f.name) for f in fields(self)}
        for key, value in names.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{key} must be a non-empty string")

        values = list(names.values())
        duplicates = sorted({v for v in values if values.count(v) > 1})
        if duplicates:
            raise ValueError(f"tab names must be unique, duplicated: {duplicates}")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Self:
        """Read the [sheet] table (optional, defaults apply when missing)."""
        return build(cls, "sheet", optional_table(raw, "sheet"))

    