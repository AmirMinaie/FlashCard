from kivy.core.text import LabelBase

def register_fonts(theme_cls):

    LabelBase.register(name="times", fn_regular="fonts/times.ttf")
    LabelBase.register(name="timesbd", fn_regular="fonts/timesbd.ttf")
    LabelBase.register(name="timesbi", fn_regular="fonts/timesbi.ttf")
    LabelBase.register(name="timesi", fn_regular="fonts/timesi.ttf")

