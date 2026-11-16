from dataclasses import dataclass, field
from typing import Any, Self


@dataclass(frozen=True, slots=True, kw_only=True)
class SheetConfig:
    tab_matches_data: str = field(default="Matches Data")
    tab_players_data: str = field(default="Players Data")
    tab_events_data: str = field(default="Events Data")
    tab_bans_data: str = field(default="Bans Data")
    tab_duo_data: str = field(default="Duo Stats")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Self:
        """Read the [sheet] table (optional, defaults apply when missing)."""
        return cls(**raw.get("sheet", {}))