from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivymd.uix.button import MDRaisedButton
from app.widgets.ApplyFont import ApplyFont

class BaseButtonA(ApplyFont, MDRaisedButton):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint_y = None
        self.height = dp(46)

        self.radius = [12, 12, 12, 12]

        self.elevation = 2

        self.font_size = "13sp"
        self.icon_size = "18sp"

        self.theme_text_color = "Custom"
        self.text_color = (1, 1, 1, 1)