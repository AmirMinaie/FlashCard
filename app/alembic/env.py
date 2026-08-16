from logging.config import fileConfig

from alembic import context

import os
import sys


# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ==========================================================
# Alembic Config
# ==========================================================

config = context.config


# ==========================================================
# Logging
# ==========================================================

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ==========================================================
# Import application database
# ==========================================================

from app.DA.base import Base
from app.DA.session import create_db_engine
from app.DA.models import *


# ==========================================================
# Metadata
# ==========================================================

target_metadata = Base.metadata


# ==========================================================
# Offline
# ==========================================================

def run_migrations_offline() -> None:

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


# ==========================================================
# Online
# ==========================================================

def run_migrations_online() -> None:

    engine = create_db_engine()

    with engine.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():

            context.run_migrations()


# ==========================================================
# Run
# ==========================================================

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()