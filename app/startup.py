from app.cmn.backup_db import backup_database
from app.DA import init_db
from app.cmn.data_migration import DataMigration

def initialize_application():
    backup_database()
    init_db()
    DataMigration.LoadOldData()