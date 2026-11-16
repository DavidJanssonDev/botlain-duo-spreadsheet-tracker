from dataclasses import dataclass, field
from typing import Any, Self

from .google_config import SheetConfig
from .riot_config import RiotSettings


@dataclass(frozen=True, slots=True, kw_only=True)
class AppConfig:
    riot: RiotSettings
    sheet: SheetConfig = field(default_factory=SheetConfig)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Self:
        return cls(
            riot=RiotSettings.from_dict(raw),
            sheet=SheetConfig.from_dict(raw),
        )