import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Self

from .google_config import SheetConfig
from .riot_config import RiotSettings


@dataclass
class AppConfig:
    riot: RiotSettings
    sheet: SheetConfig = field(default_factory=SheetConfig)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Self:
        return cls(
            riot=RiotSettings.from_dict(raw),
            sheet=SheetConfig.from_dict(raw)
        )

    @classmethod
    def load(cls, path: str | Path = "config.toml") -> Self:
        with Path(path).open("rb") as f:
            return cls.from_dict(tomllib.load(f))
