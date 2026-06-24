from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.bottomnavigation import MDBottomNavigationItem

from cmn.font_manage import FontManager


Builder.load_string('''
<MDBottomNavigationItemA>:
    icon: ""
    text: ""
    badge_text: root.badge_count
''')


class MDBottomNavigationItemA(MDBottomNavigationItem):
    icon = StringProperty("")
    text = StringProperty("")
    badge_count = NumericProperty(10)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(badge_count=self.on_badge_count)

    def on_kv_post(self, base_widget):
        # بعد از ساخته شدن ids داخلی KivyMD
        self.on_badge_count(self, self.badge_count)

    def on_badge_count(self, instance, value):
        self.update_task_badge(value)

    def update_task_badge(self, count):
        badge = self.ids.get("badge_widget")

        if not badge:
            return

        # فونت متن داخل badge
        badge.font_name = FontManager.IPA_FONT

        if count <= 0:
            badge.opacity = 0
            return

        badge.opacity = 1
        badge.text = str(count) if count <= 99 else "99+"

        if count > 20:
            badge.md_bg_color = (0.8, 0.1, 0.1, 1)
        else:
            badge.md_bg_color = (1, 0.2, 0.2, 1)