from kivy.lang import Builder
from kivymd.uix.bottomnavigation import  MDBottomNavigation , MDBottomNavigationItem 
from kivy.properties import StringProperty , ColorProperty , NumericProperty
from kivymd.uix.card import MDCard
from kivy.metrics import dp


Builder.load_string ('''

<MDBottomNavigationItemA>:
    icon: ""
    text: ""
    badge_text : root.badge_count

''')

class MDBottomNavigationItemA (MDBottomNavigationItem):
    icon = StringProperty()
    text = StringProperty()
    badge_count = NumericProperty(10)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(badge_count=self.on_badge_count)

    def on_badge_count(self, instance, value):
        """وقتی badge_count تغییر کرد"""
        self.update_task_badge(value)

    def update_task_badge(self, count):
        """آپدیت بدج با پشتیبانی کامل از اعداد"""
        badge = self.ids.badge_widget
        
        if count <= 0:
            badge.opacity = 0
        else:
            badge.opacity = 1
            if count <= 99:
                badge.text = str(count)
            else:
                badge.text = "99+"
            
            # تغییر رنگ بر اساس مقدار
            if count > 20:
                badge.md_bg_color = (0.8, 0.1, 0.1, 1)  # قرمز تیره
            else:
                badge.md_bg_color = (1, 0.2, 0.2, 1)  # قرمز معمولی