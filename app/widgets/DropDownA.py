from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty, ListProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.button import MDFlatButton
from widgets.ApplyFont import ApplyFont

Builder.load_string('''
<DropDownA>:
    orientation: "vertical"
    size_hint_y: None
    height: dp(76)
    spacing: "2dp"
    padding: "8dp"
    adaptive_height: True
    
    MDLabelA:
        text: root.text_h + (" *" if root.is_required else "")
        size_hint_y: None
        height: dp(20)
        font_style: "Caption"
        theme_text_color: "Custom"
        text_color: (0.9, 0.2, 0.2, 0.9) if root.is_required and not root.selected_value else (0.5, 0.5, 0.5, 1)
        padding: "12dp", 0
    
    MDBoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: dp(46)
        spacing: "0dp"
        md_bg_color: (0.95, 0.95, 0.95, 1)
        radius: [dp(10)]
        padding: "4dp", 0
        
        MDIcon:
            icon: root.icon
            size_hint_x: None
            width: dp(32)
            pos_hint: {"center_y": 0.5}
            theme_text_color: "Custom"
            text_color: (0.9, 0.2, 0.2, 0.9) if root.is_required and not root.selected_value else (0.5, 0.5, 0.5, 1)
        
        MDLabelA:
            id: dropdown_btn
            text: root.selected_value if root.selected_value else "Select..."
            size_hint_x: 1
            pos_hint: {"center_y": 0.5}
            halign: "left"
            valign: "middle"
            theme_text_color: "Custom"
            text_color: (0, 0, 0, 1) if root.selected_value else (0.45, 0.45, 0.45, 1)
            shorten: True
            shorten_from: "right"
            padding: "8dp", 0
        
        MDIcon:
            icon: "chevron-down"
            size_hint_x: None
            width: dp(28)
            pos_hint: {"center_y": 0.5}
            theme_text_color: "Custom"
            text_color: (0.4, 0.4, 0.4, 1)
            padding: "0dp", 0
''')

class IconListItem(OneLineIconListItem):
    """آیتم سفارشی برای منوی دراپ‌داون"""
    icon = StringProperty("circle-small")
    icon_color = ListProperty([0.5, 0.5, 0.5, 0.6])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.icon_widget = IconLeftWidget(
            icon=self.icon,
            theme_text_color="Custom",
            text_color=self.icon_color
        )
        self.add_widget(self.icon_widget)
        
        self.bind(icon=self._update_icon)
        self.bind(icon_color=self._update_icon_color)
    
    def _update_icon(self, instance, value):
        self.icon_widget.icon = value
    
    def _update_icon_color(self, instance, value):
        self.icon_widget.text_color = value

class DropDownA(MDBoxLayout):
    text_h = StringProperty("title")
    icon = StringProperty("message")
    selected_value = StringProperty("")
    selected_Id = NumericProperty(0)
    item_menu = ObjectProperty(None)
    is_required = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pos_menu = None
        self.bind(
            selected_value=self._update_text,
            is_required=self._update_appearance
        )
        self.bind(pos=self._update_touch_area)
    
    def _update_touch_area(self, *args):
        pass
    
    def _update_text(self, *args):
        if hasattr(self, 'ids') and 'dropdown_btn' in self.ids:
            self.ids.dropdown_btn.text = self.selected_value if self.selected_value else "Select..."
    
    def _update_appearance(self, *args):
        pass
    
    def on_touch_down(self, touch):
        # بررسی کلیک روی باکس دراپ‌داون
        if self.ids.dropdown_btn.collide_point(*touch.pos):
            self.on_dropdown_click()
            return True
        return super().on_touch_down(touch)
    
    def on_dropdown_click(self, *args):
        if self.item_menu:
            items = self.item_menu
            
            if not items:
                return
            
            menu_items = []
            for item in items:
                is_selected = item['id'] == self.selected_Id
                
                def make_callback(item=item):
                    return lambda: self.set_selected_value(item)
                
                menu_items.append({
                    "viewclass": "IconListItem",
                    "text": item['caption'],
                    "icon": "check" if is_selected else "circle-small",
                    "icon_color": [0.2, 0.6, 1, 1] if is_selected else [0.5, 0.5, 0.5, 0.6],
                    "height": dp(48),
                    "on_release": make_callback(),
                })
            
            if self.pos_menu:
                self.pos_menu.dismiss()
            
            self.pos_menu = MDDropdownMenu(
                caller=self.ids.dropdown_btn,
                items=menu_items,
                width_mult=3.5,
                max_height=dp(240),
                border_margin=dp(12),
                radius=[dp(12)],
                elevation=8,
                ver_growth="down",
                hor_growth="right",
            )
            
            self.pos_menu.open()
    
    def set_selected_value(self, item):
        self.selected_value = item['caption']
        self.selected_Id = item['id']
        
        if self.pos_menu:
            self.pos_menu.dismiss()
            self.pos_menu = None
    
    def validate(self):
        if self.is_required and not self.selected_value:
            return False, f"{self.text_h} is required"
        return True, ""

    def clear_selection(self):
        self.selected_value = ""
        self.selected_Id = 0

    def set_selected_by_id(self, item_id):
        if not self.item_menu:
            return
        
        for item in self.item_menu:
            if item["id"] == item_id:
                self.selected_Id = item["id"]
                self.selected_value = item["caption"]
                return