import sys
from pathlib import Path
import shutil


class PathManager:
    APP_NAME = "DuckMemo"

    @classmethod
    def get_data_dir(cls) -> Path:
        return Path.home() / "Documents" / cls.APP_NAME

    @classmethod
    def base_dir(cls) -> Path:
        """
        ریشه پروژه در حالت توسعه.
        فرض: این فایل دو پوشه پایین‌تر از ریشه پروژه است.
        """
        return Path(__file__).resolve().parents[2]

    @classmethod
    def bundled_path(cls , *relative_path: str) -> Path:
        """
        مسیر فایل‌های همراه برنامه:
        - در exe: داخل _MEIPASS
        - در توسعه: داخل ریشه پروژه
        """
        if getattr(sys, "frozen", False):
            return Path(sys._MEIPASS, *relative_path)

        return cls.base_dir().joinpath(*relative_path)

    @classmethod
    def app_path(cls, *relative_path: str) -> Path:
        """
        فقط برای فایل‌های داخل app در حالت توسعه.
        در بیلد، app حذف شده و محتوا مستقیم داخل bundle قرار می‌گیرد.
        """
        if getattr(sys, "frozen", False):
            return Path(sys._MEIPASS).joinpath(*relative_path)

        return cls.base_dir() / "app" / Path(*relative_path)

    @staticmethod
    def copy_missing_files(source_dir: Path, target_dir: Path) -> None:
        if not source_dir.exists():
            raise FileNotFoundError(
                f"Default config folder not found: {source_dir}"
            )

        target_dir.mkdir(parents=True, exist_ok=True)

        for source_item in source_dir.rglob("*"):
            relative_path = source_item.relative_to(source_dir)
            target_item = target_dir / relative_path

            if source_item.is_dir():
                target_item.mkdir(parents=True, exist_ok=True)

            elif not target_item.exists():
                target_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_item, target_item)

    @classmethod
    def initialize(cls) -> None:
        # مسیر قابل‌نوشتن کاربر
        cls.DATA_DIR = cls.get_data_dir()
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)

        # config قابل‌تغییر کاربر
        cls.CONFIG_DIR = cls.DATA_DIR / "config"

        # configهای اولیه که همراه برنامه بیلد شده‌اند
        default_config_dir = cls.app_path(
            "assets",
            "defaults",
            "config"
        )

        cls.copy_missing_files(default_config_dir, cls.CONFIG_DIR)

        # سایر فایل‌های قابل‌تغییر کاربر
        cls.FILES_DIR = cls.DATA_DIR / "files"
        cls.BACKUP_DIR = cls.DATA_DIR / "backups"

        cls.FILES_DIR.mkdir(parents=True, exist_ok=True)
        cls.BACKUP_DIR.mkdir(parents=True, exist_ok=True)


PathManager.initialize()