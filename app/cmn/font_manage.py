from kivy.core.text import LabelBase
from app.cmn.resource_helper import PathManager
from app.cmn.config_reader import ConfigReader
from app.cmn.logger import logger


class FontManager:
    DEFAULT_FONT = None
    IPA_FONT = None
    REQUIRED_STYLES = ["regular", "bold"]
    FONT_DIR = "assets/fonts"
    _registered = False

    @classmethod
    def register_fonts(self):
        if self._registered:
            return

        self.DEFAULT_FONT = ConfigReader().get("DEFAULT_FONT",None)
        self.IPA_FONT = ConfigReader().get("IPA_FONT",None)

        if self.DEFAULT_FONT is None or self.IPA_FONT is None:
            raise ValueError("DEFAULT_FONT and IPA_FONT must be configured.")

        font_kwargs = {}
        for style in self.REQUIRED_STYLES:
            arg = f"fn_{style}"
            full_path = PathManager.app_path(
                self.FONT_DIR ,
                self.DEFAULT_FONT, 
                f"{self.DEFAULT_FONT}-{style}.ttf")
            if not full_path.exists():
                raise FileNotFoundError(f"Fonts directory not found: {str(full_path)}")

            font_kwargs[arg] = full_path.__str__()

            
        LabelBase.register(name=self.DEFAULT_FONT,**font_kwargs)

        Ipafont_kwargs = {}
        for style in self.REQUIRED_STYLES:
            arg = f"fn_{style}"
            full_path = PathManager.app_path(
                self.FONT_DIR ,
                self.IPA_FONT, 
                f"{self.IPA_FONT}-{style}.ttf")
            if not full_path.exists():
                raise FileNotFoundError(f"Fonts directory not found: {str(full_path)}")

            Ipafont_kwargs[arg] = full_path.__str__()

            
        LabelBase.register(name=self.IPA_FONT,**Ipafont_kwargs)

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
                theme_cls.font_styles[style_name][0] = self.DEFAULT_FONT