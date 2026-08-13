import importlib
import inspect
import re

from app.cmn.config_reader import ConfigReader
from app.cmn.logger import logger
from app.cmn.resource_helper import PathManager

from app.DA.session import get_session
from app.DA.base import Base


class DataMigration:

    @staticmethod
    def LoadOldData():

        old_data_path = PathManager.CONFIG_DIR / "OldData.json"

        if not old_data_path.exists():
            return

        load_old_data = ConfigReader("config.json").get("loadOldData",1)

        if load_old_data != 1:
            return

        try:
            data = ConfigReader("OldData.json").get_all()

            if not isinstance(data, dict):
                logger.error("OldData.json must contain a JSON object.")
                return

            session = get_session()

            try:
                DataMigration._migrate( session=session, data=data )

                session.commit()
                ConfigReader("config.json").set("loadOldData",0)
                logger.info("Old data migration completed successfully.")

            except Exception as e:
                session.rollback()
                logger.error(f"Old data migration failed: {e}")
                raise

            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error loading OldData.json: {e}")

    @staticmethod
    def _migrate(session, data):

        id_maps = {}
        models = DataMigration._discover_models()

        for entity_name, rows in data.items():

            if not isinstance(rows, list):
                continue

            model = DataMigration._find_model(entity_name,models)

            if model is None:
                logger.warning(f"No DA model found for entity: {entity_name}")
                continue

            id_maps[entity_name] = {}

            for row in rows:
                try:
                    old_id = row.get("id")

                    values = DataMigration._prepare_values(session=session,row=row,model=model,id_maps=id_maps)
                    obj = model(**values)
                    session.add(obj)

                    session.flush()

                    new_id = obj.id

                    if old_id is not None:
                        id_maps[entity_name][old_id] = new_id

                    logger.info(f"Migrated {entity_name}: "f"{old_id} -> {new_id}")

                except Exception as e:
                    logger.error(f"Error migrating "f"{entity_name} row {row}: {e}")
                    raise

    @staticmethod
    def _prepare_values(session,row,model,id_maps):

        values = {}
        columns = {
            column.name: column
            for column in model.__table__.columns
        }

        for key, value in row.items():

            if key == "id":
                continue

            column_name = DataMigration._resolve_column_name(key,columns)

            if column_name is None:
                logger.error(f"Column not found for key '{key}'. "f"Available columns: {columns}")
                raise ValueError( f"Column not found for key '{key}'. " f"Available columns: {columns}")

            if column_name is None:
                continue

            column = columns[column_name]

            if column.foreign_keys:
                value = DataMigration._resolve_foreign_key(session=session,key=key,value=value,column=column,id_maps=id_maps)

            values[column_name] = value

        return values

    @staticmethod
    def _resolve_column_name(key, columns):


        if key in columns:
            return key

        snake_key = re.sub(
            r'(?<!^)(?=[A-Z])',
            '_',
            key
        ).lower()

        for column_name in columns:

            normalized = re.sub(
                r'(?<!^)(?=[A-Z])',
                '_',
                column_name
            ).lower()

            if normalized == snake_key:
                return column_name

        return None

    # ---------------------------------------------------------
    # Foreign Key resolver
    # ---------------------------------------------------------

    @staticmethod
    def _resolve_foreign_key(session,key,value,column,id_maps):

        if value is None:
            return None

        # ---------------------------------------------
        # Already numeric
        # ---------------------------------------------

        if isinstance(value, int):
            return value

        # ---------------------------------------------
        # Example:
        #
        # flashcard_id = 10
        # book_id = 2
        # schedule_id = 1
        # ---------------------------------------------

        if key.endswith("_id"):

            referenced_table = (
                next(iter(column.foreign_keys))
                .target_fullname
                .split(".")[0]
            )

            source_entity = DataMigration._table_to_entity(
                referenced_table
            )

            mapping = id_maps.get(
                source_entity,
                {}
            )

            if value in mapping:
                return mapping[value]

        target_table = (
            next(iter(column.foreign_keys))
            .target_fullname
            .split(".")[0]
        )

        if target_table == "constant":

            return DataMigration._get_constant_id(
                session=session,
                value=value,
                column_name=key
            )

        return value

    # ---------------------------------------------------------
    # Constant
    # ---------------------------------------------------------

    @staticmethod
    def _get_constant_id(session,value,column_name=None):

        if value is None or value == '':
            return None

        from DA.models.constantDA import constantDA

        name = str(value).strip().lower().replace(
            " ",
            "_"
        )

        query = session.query(constantDA).filter(constantDA.name == name)
        constant = query.first()
        if constant is None:
            raise ValueError(f"Constant not found: "f"{name} "f"(field={column_name})")

        return constant.id

    # ---------------------------------------------------------
    # Discover all DA models
    # ---------------------------------------------------------

    @staticmethod
    def _discover_models():

        import DA.models

        models = {}

        for name, obj in inspect.getmembers(
            DA.models,
            inspect.isclass
        ):

            if not name.endswith("DA"):
                continue

            table_name = obj.__tablename__

            models[table_name] = obj

        return models

    # ---------------------------------------------------------
    # Find model from JSON entity name
    # ---------------------------------------------------------

    @staticmethod
    def _find_model(
        entity_name,
        models
    ):

        table_name = DataMigration._entity_to_table(
            entity_name
        )

        return models.get(table_name)

    # ---------------------------------------------------------
    # JSON entity -> DB table
    # ---------------------------------------------------------

    @staticmethod
    def _entity_to_table(entity_name):

        # studyScheduleItems
        # -> studyScheduleItem

        if entity_name.endswith("ies"):
            entity_name = (
                entity_name[:-3] + "y"
            )

        elif entity_name.endswith("s"):
            entity_name = entity_name[:-1]

        return entity_name

    # ---------------------------------------------------------
    # DB table -> JSON entity
    # ---------------------------------------------------------

    @staticmethod
    def _table_to_entity(table_name):

        return table_name + "s"