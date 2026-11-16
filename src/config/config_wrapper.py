import tomllib
from pathlib import Path

from ..errors.config import ConfigError
from .app_config import AppConfig

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_config(path: str | Path ="config.toml") -> AppConfig:
    """Load config.toml. Relative paths are resolved from the project root."""

    path = Path(path)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    try:
        with path.open("rb") as f:
            raw = tomllib.load(f)
    except FileNotFoundError:
        raise ConfigError(f"config file not found: {path}") from None
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"invalid TOML in {path}: {e}") from e

    try:
        return AppConfig.from_dict(raw)
    except ConfigError as e:
        raise ConfigError(f"{path.name}: {e}") from None