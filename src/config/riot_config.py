from dataclasses import dataclass, field
from datetime import date
from typing import Any, Self

from ..errors.config import ConfigError, build, require_table

PLATFORM_TO_REGIONN: dict[str, str] = {
    # americas
    "na1": "americas", "br1": "americas", "la1": "americas", "la2": "americas",
    # asia
    "kr": "asia", "jp1": "asia",
    # europe
    "euw1": "europe", "eun1": "europe", "tr1": "europe", "ru": "europe", "me1": "europe",
    # sea
    "oc1": "sea", "ph2": "sea", "sg2": "sea", "th2": "sea", "tw2": "sea", "vn2": "sea",
}


@dataclass(frozen=True, slots=True, kw_only=True)
class RiotApiConfig:
    platform: str

    def __post_init__(self) -> None:
        platform = self.platform.strip().lower()
        if platform not in PLATFORM_TO_REGIONN:
            valid = ", ".join(sorted(PLATFORM_TO_REGIONN))
            raise ValueError(f"unknown platform {self.platform!r}. Valid: {valid}")
        object.__setattr__(self, "platform", platform)

    @property
    def region(self) -> str:
        return PLATFORM_TO_REGIONN[self.platform]

@dataclass(frozen=True, slots=True, kw_only=True)
class PlayerRef:
    name: str
    tag: str

    def __post_init__(self) -> None:
        name = self.name.strip()
        tag = self.tag.strip().lstrip("#")

        if not name:
            raise ValueError("name must not be empty")

        if not tag:
            raise ValueError("tag must not be empty")

        object.__setattr__(self, "name", name)
        object.__setattr__(self, "tag", tag)

@dataclass(frozen=True, slots=True, kw_only=True)
class DuoConfig:
    adc: PlayerRef
    support: PlayerRef

    def __post_init__(self) -> None:
        if self.adc == self.support:
            raise ValueError("adc and support must be different players")

    @classmethod    
    def from_dict(cls, data: dict[str, Any]) -> Self:
        adc = build(PlayerRef, "duo.adc", require_table(data, "adc", parent="duo"))
        support = build(PlayerRef, "duo.support", require_table(data, "support", parent="duo"))

        try:
            return cls(adc=adc, support=support)
        except ValueError as e:
            raise ConfigError(f"[duo] {e}") from e

@dataclass(frozen=True, slots=True, kw_only=True)
class FilterConfig:
    start_date: date  
    queues: tuple[int, ...] = field(default_factory=tuple) 
    min_duration_seconds: int = field(default=300)

    def __post_init__(self) -> None:
        if self.start_date > date.today():
            raise ValueError("start_date must not be in the future")

        if self.min_duration_seconds < 0:
            raise ValueError("min_duration_seconds must be 0 or higher")

        if any(q <= 0 for q in self.queues):
            raise ValueError("queue ids must be positie integers")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        kwargs = dict(data)
        # TOML may give a native date or a string, accept both
        start = kwargs.get("start_date")

        if start is not None and not isinstance(start, date):
            try:
                kwargs["start_date"] = date.fromisoformat(start)
            except (TypeError, ValueError):
                raise ConfigError(f"[filter] start_date must be a date like 2026-01-01, got {start!r}") from None

        if "queues" in kwargs:
            kwargs["queues"] = tuple(kwargs["queues"])

        return build(cls, "filter", kwargs)

@dataclass(frozen=True, slots=True, kw_only=True)
class DataConfig:
    fetch_timeline: bool = field(default=True)
    snapshot_interval_minutes: int = field(default=5)
    snapshot_max_minutes: int = field(default=0)  # 0 = until the end of the game
    snapshot_include_final: bool = field(default=True)
    full_profile_for_duo: bool = field(default=True)

    def __post_init__(self) -> None:
        if self.snapshot_interval_minutes < 1:
            raise ValueError("snapshot_interval_minutes must be 1 or higher")
        if self.snapshot_max_minutes < 0:
            raise ValueError("snapshot_max_minutes must be 0 or higher")
        if 0 < self.snapshot_max_minutes < self.snapshot_interval_minutes:
            raise ValueError("snapshot_max_minutes must be 0 or at least snapshot_interval_minutes")

@dataclass(frozen=True, slots=True, kw_only=True)
class RateLimitConfig:
    requests_per_second: int = field(default=20)
    requests_per_2min: int = field(default=100)
    safety_margin: float = field(default=0.9)

    def __post_init__(self) -> None:
        if self.requests_per_second < 1:
            raise ValueError("requests_per_second must be 1 or higher")
        if self.effective_per_2min < 1:
            raise ValueError("requests_per_2min must be 1 or higher")
        if not 0 < self.safety_margin <= 1:
            raise ValueError("safety_margin must be in the range (0, 1]")

    @property
    def effective_per_second(self) -> int:
        return max(1, int(self.requests_per_second * self.safety_margin))

    @property
    def effective_per_2min(self) -> int:
        return max(1, int(self.requests_per_2min * self.safety_margin))

@dataclass(frozen=True, slots=True, kw_only=True)
class RiotSettings:
    """Everything the Riot side of the script needs."""

    api: RiotApiConfig
    duo: DuoConfig
    filter: FilterConfig
    data: DataConfig = field(default_factory=DataConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Self:
        """Read the [riot], [duo], [filter], [data] and [rate_limit] tables."""
        return cls(
            api=build(RiotApiConfig, "riot", require_table(raw, "riot")),
            duo=DuoConfig.from_dict(require_table(raw, "duo")),
            filter=FilterConfig.from_dict(require_table(raw, "filter")),
            data=build(DataConfig, "data", raw.get("data", {})),
            rate_limit=build(RateLimitConfig, "rate_limit", raw.get("rate_limit", {})),
        )