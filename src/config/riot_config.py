from dataclasses import dataclass, field
from datetime import date
from typing import Any, Self


@dataclass(frozen=True, slots=True, kw_only=True)
class RiotApiConfig:
    platform: str
    region: str



@dataclass(frozen=True, slots=True, kw_only=True)
class PlayerRef:
    name: str
    tag: str



@dataclass(frozen=True, slots=True, kw_only=True)
class DuoConfig:
    adc: PlayerRef
    support: PlayerRef

    @classmethod    
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            adc=PlayerRef(**data["adc"]),
            support=PlayerRef(**data["support"]),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class FilterConfig:
    start_date: date  # backfill no further back than this
    queues: tuple[int, ...] = field(default_factory=tuple)  # empty = all queues
    min_duration_seconds: int = field(default=300)  # skip remakes

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        kwargs = dict(data)
        start = kwargs["start_date"]
        # TOML may give a native date or a string, accept both
        if not isinstance(start, date):
            kwargs["start_date"] = date.fromisoformat(start)
        if "queues" in kwargs:
            kwargs["queues"] = tuple(kwargs["queues"])
        return cls(**kwargs)


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


@dataclass(frozen=True, slots=True, kw_only=True)
class RateLimitConfig:
    requests_per_second: int = field(default=20)
    requests_per_2min: int = field(default=100)
    safety_margin: float = field(default=0.9)

    def __post_init__(self) -> None:
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
            api=RiotApiConfig(**raw["riot"]),
            duo=DuoConfig.from_dict(raw["duo"]),
            filter=FilterConfig.from_dict(raw["filter"]),
            data=DataConfig(**raw.get("data", {})),
            rate_limit=RateLimitConfig(**raw.get("rate_limit", {})),
        )