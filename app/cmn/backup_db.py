import shutil
from datetime import datetime

from app.cmn.resource_helper import *
from app.cmn.config_reader import ConfigReader
from app.cmn.AppName import *


def backup_database(backup_type="daily"):

    config = ConfigReader("config.json")
    backup_retention_count = config.get("backup_retention_count")
    db_name = APP_NAME + ".db"

    db_path = PathManager.bundled_path( PathManager.DATA_DIR, db_name )

    if not db_path.exists():
        return False

    # ==================================================
    # Daily Backup
    # ==================================================

    if backup_type == "daily":

        today = datetime.now().strftime("%Y-%m-%d")

        backup_file = (PathManager.BACKUP_DIR/ f"{db_name}_{today}.db")

        # Already backed up today
        if backup_file.exists():
            return True

    # ==================================================
    # Migration Backup
    # ==================================================

    elif backup_type == "before_migration":

        timestamp = datetime.now().strftime( "%Y-%m-%d_%H%M%S" )
        backup_file = ( PathManager.BACKUP_DIR / f"{db_name}_{timestamp}_before_migration.db")
    else:
        raise ValueError(f"Unknown backup type: {backup_type}")

    # ==================================================
    # Create Backup
    # ==================================================

    shutil.copy2( db_path, backup_file )

    # ==================================================
    # Retention
    # ==================================================

    backups = sorted(
        PathManager.BACKUP_DIR.glob(
            f"{db_name}_*.db"
        ),
        key=lambda file: file.stat().st_mtime,
        reverse=True
    )

    for old_backup in backups[backup_retention_count:]:
        old_backup.unlink()

    return True