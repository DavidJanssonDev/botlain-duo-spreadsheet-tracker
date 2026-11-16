from dataclasses import MISSING, fields
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

class ConfigError(Exception):
    """Raised when config.toml is missing, malformed or invalid."""


def require_table(raw: dict[str, Any], name: str, parent: str | None = None) -> dict[str, Any]:
    """Get a required [table], or explain which one is missing."""
    path = f"{parent}.{name}" if parent else name
    try:
        value = raw[name]
    except KeyError:
        raise ConfigError(f"missing required table [{path}]") from None
    if not isinstance(value, dict):
        raise ConfigError(f"[{path}] must be a table, got {type(value).__name__}")
    return value

def optional_table(raw: dict[str, Any], name: str) -> dict[str, Any]:
    """Get an optional [table]. Returns {} when missing."""
    value = raw.get(name, {})
    if not isinstance(value, dict):
        raise ConfigError(f"[{name}] must be a table, got {type(value).__name__}")
    return value


def build[T: DataclassInstance](cls: type[T], section: str, data: dict[str, Any]) -> T:
    """Build a dataclass from a dict with errors that name the section."""
    all_fields = fields(cls)  
    valid = {f.name for f in all_fields}
    required = {
        f.name
        for f in all_fields
        if f.default is MISSING and f.default_factory is MISSING
    }

    unknown = set(data) - valid
    if unknown:
        raise ConfigError(
            f"[{section}] unknown key(s): {', '.join(sorted(unknown))}. "
            f"Valid keys: {', '.join(sorted(valid))}"
        )

    missing = required - set(data)
    if missing:
        raise ConfigError(
            f"[{section}] missing required key(s): {', '.join(sorted(missing))}"
        )

    try:
        return cls(**data)
    except ValueError as e: 
        raise ConfigError(f"[{section}] {e}") from e