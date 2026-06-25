import shutil
from datetime import datetime
from cmn.resource_helper import *
from cmn.config_reader import ConfigReader

def backup_database():
    config = ConfigReader("config.json")
    backup_retention_count = config.get("backup_retention_count")

    DBName = config.get("database")['DBName']
    Bb_Path = PathManager.bundled_path(PathManager.DATA_DIR, DBName)

    today = datetime.now().strftime("%Y-%m-%d")
    backup_file = PathManager.BACKUP_DIR / f"Flashcard_{today}.db"

    if Bb_Path.exists() == False:
        return False

    if backup_file.exists():
        return

    shutil.copy2(Bb_Path, backup_file)

    backups = sorted(
        PathManager.BACKUP_DIR.glob("Flashcard_*.db"),
        key=lambda file: file.stat().st_mtime,
        reverse=True
    )

    for old_backup in backups[backup_retention_count:]:
        old_backup.unlink()
