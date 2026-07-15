from kivy.lang import Builder
from kivymd.uix.button import MDIconButton

from widgets.AsyncBehavior import AsyncBehavior

Builder.load_string("""
<AsyncIconButton>:
    theme_text_color: "Custom"
    text_color: app.theme_cls.primary_color
    user_font_size: "24sp"
""")


class AsyncIconButton(AsyncBehavior, MDIconButton):
    pass