import json
from pathlib import Path

from app.cmn.logger import logger


class ConfigReader:

    def __init__(
        self,
        file_name="config.json",
        path_file_name=None,
        default=False
    ):

        from .resource_helper import PathManager

        if path_file_name is not None:

            # برای خواندن فایل Default
            self.config_path = Path(path_file_name)
            self.default_config_path = None

        else:

            # فایل Config واقعی کاربر
            self.config_path = (
                PathManager.CONFIG_DIR / file_name
            )

            # فایل Default داخل پروژه
            self.default_config_path = Path(
                PathManager.app_path(
                    "assets",
                    "defaults",
                    "config",
                    file_name
                )
            )

        self.default = default
        self._config = None

        logger.info(
            f"ConfigReader config_path: {self.config_path}"
        )

        logger.info(
            f"ConfigReader default_path: {self.default_config_path}"
        )

    # ==================================================
    # Load
    # ==================================================

    def load(self):

        logger.info(
            f"Loading config: {self.config_path}"
        )

        if not self.config_path.exists():

            raise FileNotFoundError(
                f"Config file not found: {self.config_path}"
            )

        with open(
            self.config_path,
            "r",
            encoding="utf-8"
        ) as f:

            self._config = json.load(f)

#        if self.default:
#
#            logger.info(
#                "Default config merge enabled."
#            )
#
#            self._merge_missing()

        return self._config

    # ==================================================
    # Get
    # ==================================================

    def get(self, key, default=None):

        if self._config is None:
            self.load()

        return self._config.get(
            key,
            default
        )

    # ==================================================
    # Set
    # ==================================================

    def set(self, key, value):

        if self._config is None:
            self.load()

        keys = key.split(".")

        target = self._config

        for part in keys[:-1]:

            if part not in target:
                target[part] = {}

            target = target[part]

        target[keys[-1]] = value

        logger.info(
            f"Saving config: {self.config_path}"
        )

        logger.info(
            f"Setting {key} = {value}"
        )

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

    # ==================================================
    # Merge Missing
    # ==================================================

    def _merge_missing(self):

        if self.default_config_path is None:

            logger.warning(
                "Default config path is None."
            )

            return False

        if not self.default_config_path.exists():

            logger.warning(
                f"Default config not found: "
                f"{self.default_config_path}"
            )

            return False

        # ==========================================
        # Load default file directly
        # ==========================================

        with open(
            self.default_config_path,
            "r",
            encoding="utf-8"
        ) as f:

            default_config = json.load(f)

        # ==========================================
        # Versions
        # ==========================================

        old_version = self._config.get(
            "config_file_vertion",
            0
        )

        new_version = default_config.get(
            "config_file_vertion",
            0
        )

        logger.info(
            f"Config version: "
            f"current={old_version}, "
            f"default={new_version}"
        )

        # ==========================================
        # Nothing to do
        # ==========================================

        if old_version >= new_version:

            logger.info(
                "Config is already up to date."
            )

            return False

        # ==========================================
        # Add missing fields
        # ==========================================

        changed = False

        for key, default_value in default_config.items():

            if key not in self._config:

                logger.info(
                    f"Adding missing config field: "
                    f"{key} = {default_value}"
                )

                self._config[key] = default_value

                changed = True

        # ==========================================
        # Update version
        # ==========================================

        self._config["config_file_vertion"] = new_version

        changed = True

        # ==========================================
        # Save
        # ==========================================

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

        logger.info(
            f"Config updated successfully: "
            f"{self.config_path}"
        )

        return changed