from app.cmn.backup_db import backup_database
from app.DA import init_db
from app.cmn.data_migration import DataMigration
from app.cmn.migration_manager import migrate_database
from app.cmn.config_reader import ConfigReader
from app.cmn.version import DB_VERSION
from app.cmn.logger import logger


def initialize_application():

    try:

        backup_database()

        config = ConfigReader("config.json")
        database_config = config.get("database")
        current_db_version = int( database_config.get("version", 0) )

        logger.info( f"Database version: " f"{current_db_version} | " f"Application DB version: {DB_VERSION}" )

        # ==========================================
        # Database Migration
        # ==========================================

        if current_db_version < DB_VERSION:

            logger.info( f"Database migration required: " f"{current_db_version} -> {DB_VERSION}" )

            # Backup specifically before migration
            if backup_database("before_migration") is False:
                raise RuntimeError( "Database backup before migration failed." )

            if not migrate_database():
                raise RuntimeError( "Database migration failed." )

            # ==========================================
            # Update Database Version
            # ==========================================
            config.set("database.version", DB_VERSION)
            logger.info(
                f"Database migration completed: "
                f"{current_db_version} -> {DB_VERSION}"
            )

        else:
            logger.info( "Database migration not required.")

        init_db()
        DataMigration.LoadOldData()


    except Exception as error:
        logger.exception( f"Error initializing application: {error}")
        raise