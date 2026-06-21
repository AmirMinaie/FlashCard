from kivymd.uix.label import MDLabel


class MDLabelA(MDLabel):

    def __init__(self, style="title", haligna="left", **kwargs):

        kwargs["font_name"] = "IPAFont"

        if style == "title":
            kwargs["font_size"] = "24sp"
            kwargs["halign"] = haligna

        elif style == "subtitle":
            kwargs["font_size"] = "18sp"
            kwargs["halign"] = haligna

        super().__init__(**kwargs)