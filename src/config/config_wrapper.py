

from pathlib import Path

from .app_config import AppConfig


class ProjectConfig:
    def __init__(self, config_file_name: str) -> None:
        parent_folder = Path(__file__).resolve().parent
        self.config_file: Path = parent_folder / config_file_name
        self.config_data: AppConfig = AppConfig.load(self.config_file)