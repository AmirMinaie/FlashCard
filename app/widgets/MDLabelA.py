from kivymd.uix.label import MDLabel
from app.widgets.ApplyFont import ApplyFont

class MDLabelA(ApplyFont, MDLabel):

    def __init__(self, style="title", haligna="left", **kwargs):
        super().__init__(**kwargs)