from cmn.font_manage import FontManager

class ApplyFont:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if hasattr(self, "font_name"):
            self.font_name = FontManager.DEFAULT_FONT
