from kivymd.uix.label import MDLabel

class MDLabelA(MDLabel):
    def __init__(self, style="title" ,haligna = "left", **kwargs):

        if style == "title":
            kwargs["font_size"] = "24sp"
            kwargs["halign"] = haligna
#            kwargs["font_name"] = "timesbd"
#            kwargs["font_name"] = "its"

        elif style == "subtitle":
            kwargs["font_size"] = "18sp"
            kwargs["halign"] = haligna
#            kwargs["font_name"] = "times"
#            kwargs["font_name"] = "its"

        else:
#            kwargs["font_name"] = "its"
            pass

        super().__init__(**kwargs)

