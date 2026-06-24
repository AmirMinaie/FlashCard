from kivymd.uix.label import MDLabel
from cmn.font_manage import FontManager


class MDLabelA(MDLabel):

    def __init__(self, style="title", haligna="left", **kwargs):

        kwargs.setdefault("font_name", FontManager.DEFAULT_FONT)


        super().__init__(**kwargs)