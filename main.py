import sys

from src.config import load_config
from src.errors.config import ConfigError


def main() -> int:
    try:
        config = load_config("config.toml")
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1

    print(config.riot.api.platform, config.riot.api.region)
    return 0


if __name__ == "__main__":
    sys.exit(main())