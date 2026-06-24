from kivy.lang import Builder
from kivy.properties import BooleanProperty, ColorProperty, StringProperty
from kivymd.uix.textfield import MDTextField

from cmn.font_manage import FontManager


Builder.load_string('''
<MDTextFieldA>:
    hint_text: root.text_h + (" *" if root.is_required else "")
    icon_left: root.icon

    hint_text_color: root.required_color if root.is_required and not self.text else (0.5, 0.5, 0.5, 1)
    line_color_normal: root.required_color if root.is_required and not self.text else (0, 0, 0, 1)

    text_color: 0, 0, 0, 1
    line_color_focus: app.theme_cls.primary_color

    size_hint_y: None
    height: dp(60)
''')


class MDTextFieldA(MDTextField):
    text_h = StringProperty("")
    icon = StringProperty("")
    is_required = BooleanProperty(False)
    required_color = ColorProperty([1, 0, 0, 1])

    def __init__(self, **kwargs):
        # فونت ثبت‌شده مثل "NotoSans" را می‌دهد، نه متن DEFAULT_FONT
        kwargs.setdefault("font_name", FontManager.DEFAULT_FONT)
        super().__init__(**kwargs)