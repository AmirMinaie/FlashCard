from kivy.core.text import LabelBase
from cmn.resource_helper import PathManager
from cmn.config_reader import ConfigReader
from cmn.logger import logger


class FontManager:
    FONT_NAME = None
    REQUIRED_STYLES = ["regular", "bold"]
    FONT_DIR = "assets/fonts"
    _registered = False

    @classmethod
    def register_fonts(self):
        if self._registered:
            return

        self.FONT_NAME = ConfigReader().get("DEFAULT_FONT",None)
        if self.FONT_NAME is None:
            raise ValueError("Set DEFAULT_FONT in Config")

        font_kwargs = {}
        for style in self.REQUIRED_STYLES:
            arg = f"fn_{style}"
            full_path = PathManager.app_path(
                self.FONT_DIR ,
                self.FONT_NAME, 
                f"{self.FONT_NAME}-{style}.ttf")
            if not full_path.exists():
                raise FileNotFoundError(f"Fonts directory not found: {str(full_path)}")

            font_kwargs[arg] = full_path.__str__()

            
        LabelBase.register(name=self.FONT_NAME,**font_kwargs)

        self._registered = True

    @classmethod
    def apply_kivymd_default_font(self, theme_cls):
        
        font_styles = (
            "H1",
            "H2",
            "H3",
            "H4",
            "H5",
            "H6",
            "Subtitle1",
            "Subtitle2",
            "Body1",
            "Body2",
            "Button",
            "Caption",
            "Overline",
        )

        for style_name in font_styles:
            if style_name in theme_cls.font_styles:
                theme_cls.font_styles[style_name][0] = self.FONT_NAME