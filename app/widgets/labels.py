from kivymd.uix.label import MDLabel

class MDLabelA(MDLabel):
    def __init__(self, style="title", **kwargs):
        if style == "title":
            kwargs["font_size"] = "24sp"
            kwargs["halign"] = "center"
            kwargs["font_name"] = "timesbd"
        elif style == "subtitle":
            kwargs["font_size"] = "18sp"
            kwargs["halign"] = "center"
            kwargs["font_name"] = "times"
        super().__init__(**kwargs)
