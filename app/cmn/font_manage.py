from kivy.core.text import LabelBase
from cmn.resource_helper import PathManager


class FontManager:
    DEFAULT_FONT = "CharisSIL"

    _registered = False

    @classmethod
    def register_fonts(cls):
        """
        فونت‌ها را فقط یک بار در کل اجرای برنامه ثبت می‌کند.
        این متد باید قبل از Builder.load_file اجرا شود.
        """
        if cls._registered:
            return

        LabelBase.register(
            name=cls.DEFAULT_FONT,
            fn_regular=PathManager.app_path( "assets", "fonts", "CharisSIL-Regular.ttf"
            ).__str__(),
            fn_bold=PathManager.app_path("assets", "fonts", "CharisSIL-Bold.ttf"
            ).__str__(),
        )

        cls._registered = True

    @classmethod
    def apply_kivymd_default_font(cls, theme_cls):
        
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
                theme_cls.font_styles[style_name][0] = cls.DEFAULT_FONT