import sys
from alembic.config import Config
from alembic import command
from app.cmn.logger import logger


def migrate_database():

    logger.info("=" * 60)
    logger.info("Starting database migration")
    logger.info("=" * 60)

    # ==================================================
    # 2. Alembic configuration
    # ==================================================

    try:

        alembic_config = Config(
            "alembic.ini"
        )

        # ==================================================
        # 3. Run migration
        # ==================================================

        logger.info(
            "Running Alembic upgrade head..."
        )

        command.upgrade(
            alembic_config,
            "head"
        )

    except Exception as error:

        logger.exception(
            f"Database migration failed: {error}"
        )

        return False

    # ==================================================
    # 4. Success
    # ==================================================

    logger.info("Database migration completed successfully.")
    logger.info("=" * 60)

    return True