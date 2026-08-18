import json
from pathlib import Path

from app.cmn.logger import logger


class ConfigReader:
    _instances = {}

    def __new__(cls, file_name="config.json"):
        key = str(file_name)

        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance

        return cls._instances[key]

    def __init__(self, file_name="config.json"):
        if getattr(self, "_initialized", False):
            return

        from .resource_helper import PathManager

        self.file_name = file_name

        self.config_path = (PathManager.CONFIG_DIR / file_name)

        self.default_config_path = Path(
            PathManager.app_path( "assets", "defaults", "config", file_name )
        )

        self._config = None
        self._loaded = False

        self._initialized = True

        logger.info(f"ConfigReader created: {self.config_path}")
        logger.debug(f"Default config path: "f"{self.default_config_path}")


    def load(self):

        if self._loaded:
            logger.debug(f"Using in-memory config: {self.config_path}")
            return self._config

        logger.info(f"Loading config from disk: {self.config_path}")

        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: "f"{self.config_path}")

        with open( self.config_path, "r", encoding="utf-8" ) as f:
            self._config = json.load(f)

        self._merge_missing()
        self._loaded = True

        logger.info( f"Config loaded successfully: " f"{self.config_path}" )

        return self._config

    def get(self, key, default=None):

        if not self._loaded:
            self.load()

        keys = key.split(".")
        value = self._config

        for part in keys:

            if not isinstance(value, dict):
                return default

            if part not in value:
                return default

            value = value[part]

        return value

    def set(self, key, value):

        if not self._loaded:
            self.load()

        keys = key.split(".")
        target = self._config

        for part in keys[:-1]:

            if part not in target:
                target[part] = {}

            elif not isinstance(target[part], dict):
                raise TypeError( f"Cannot create nested config key " f"'{key}': '{part}' is not a dictionary." )

            target = target[part]

        target[keys[-1]] = value
        logger.info(f"Setting config: {key} = {value}")
        self._save()

    def _save(self):

        self.config_path.parent.mkdir(parents=True,exist_ok=True)

        with open(
            self.config_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self._config,
                f,
                ensure_ascii=False,
                indent=2
            )

        logger.debug(f"Config saved: {self.config_path}")

    def clear_cache(self):

        logger.debug(f"Clearing config cache: "f"{self.config_path}")

        self._config = None
        self._loaded = False

    @classmethod
    def remove_instance(cls, file_name="config.json"):
        key = str(file_name)
        instance = cls._instances.pop(key, None)
        if instance is not None:

            logger.debug( f"ConfigReader instance removed: " f"{file_name}" )

    @classmethod
    def clear_all(cls):

        logger.debug("Clearing all ConfigReader instances.")

        for instance in cls._instances.values():

            instance._config = None
            instance._loaded = False

        cls._instances.clear()

    def _merge_missing(self):

        if not self.default_config_path.exists():
            logger.warning( f"Default config not found: " f"{self.default_config_path}" )
            return False

        with open(self.default_config_path,"r",encoding="utf-8") as f:
            default_config = json.load(f)


        old_version = self._config.get("file_vertion",0)
        new_version = default_config.get("file_vertion",0)

        logger.info( f"Config version: " f"current={old_version}, " f"default={new_version}" )

        if old_version >= new_version:

            logger.debug("Config is already up to date.")

            return False


        changed = False

        for key, default_value in default_config.items():

            if key not in self._config:

                logger.info( f"Adding missing config field: " f"{key} = {default_value}" )
                self._config[key] = default_value
                changed = True


        if self._config.get("file_vertion") != new_version:
            self._config["file_vertion"] = new_version

            changed = True

        if changed:
            self._save()
            logger.info( f"Config updated successfully: " f"{self.config_path}" )

        return changed