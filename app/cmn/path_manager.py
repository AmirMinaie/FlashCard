from pathlib import Path
from .config_reader import ConfigReader


class PathManager:
    APP_NAME = "FlashCard"
    config = ConfigReader()

    @classmethod
    def get_default_data_dir(cls):
        return Path.home() / "Documents" / cls.APP_NAME

    @classmethod
    def get_data_dir(cls):
        saved_path = cls.config.get("data_directory", "")

        if saved_path:
            path = Path(saved_path)

            if path.exists() and path.is_dir():
                return path

        default_path = cls.get_default_data_dir()
        default_path.mkdir(parents=True, exist_ok=True)

        cls.config.set("data_directory", str(default_path))

        return default_path


PathManager.DATA_DIR = PathManager.get_data_dir()
PathManager.DB_PATH = PathManager.DATA_DIR 
PathManager.FILES_DIR = PathManager.DATA_DIR / "files"
PathManager.BACKUP_DIR = PathManager.DATA_DIR / "backups"

PathManager.FILES_DIR.mkdir(parents=True, exist_ok=True)
PathManager.BACKUP_DIR.mkdir(parents=True, exist_ok=True)