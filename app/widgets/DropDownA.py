from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu

Builder.load_string('''
<DropDownA>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(50)
    spacing: "10dp"
    
    MDIcon:
        id: field_icon
        icon: root.icon
        size_hint_x: 0.1
        theme_text_color: "Secondary"
        valign: "center"
        pos_hint: {"center_y": 0.5}
        color: (0.8, 0, 0, 0.8) if root.is_required and not root.selected_value else (0.5, 0.5, 0.5, 1)
    
    BoxLayout:
        orientation: "vertical"
        size_hint_x: 0.9
        pos_hint: {"center_y": 0.5}
        
        MDLabel:
            id: hint_label
            text: root.text_h + (" *" if root.is_required else "")
            font_style: "Caption"
            size_hint_y: None
            height: dp(20)
            color: (0.8, 0, 0, 0.8) if root.is_required and not root.selected_value else (0.5, 0.5, 0.5, 1)
        
        MDRectangleFlatButton:
            id: dropdown_btn
            text: root.selected_value if root.selected_value else "Select..."
            halign: "left"
            size_hint_y: None
            height: dp(40)
            line_color: (0.8, 0, 0, 0.5) if root.is_required and not root.selected_value else (0, 0, 0, 0.2)
            text_color: (0, 0, 0, 1) if root.selected_value else (0.6, 0.6, 0.6, 1)
            pos_hint: {"center_y": 0.5}
            on_release: root.on_dropdown_click()
''')

class DropDownA(MDBoxLayout):
    text_h = StringProperty("title")
    icon = StringProperty("message")
    selected_value = StringProperty("")
    selected_Id = NumericProperty(0)
    item_menu = ObjectProperty(None)
    is_required = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            selected_value=self._update_appearance,
            is_required=self._update_appearance
        )
    
    def _update_appearance(self, *args):
        pass
    
    def on_dropdown_click(self):
        if self.item_menu:
            items = self.item_menu
            
            if not items:
                return
            
            menu_items = [
                {
                    "text": item['caption'],
                    "icon": "check" if item['id'] == self.selected_Id else "circle-outline",
                    "viewclass": "OneLineIconListItem",
                    "on_release": lambda x=item: self.set_selected_value(x),
                    "height": dp(50),
                } for item in items
            ]
            
            dropdown_btn = self.ids.dropdown_btn
            self.pos_menu = MDDropdownMenu(
                caller=dropdown_btn,
                items=menu_items,
                width_mult=4,
            )
            self.pos_menu.open()
    
    def set_selected_value(self, item):
        self.selected_value = item['caption']
        self.selected_Id = item['id']
                
        if self.pos_menu:
            self.pos_menu.dismiss()
    
    def validate(self):
        if self.is_required and not self.selected_value:
            return False, f"{self.text_h} is required"
        return True, ""

    def clear_selection(self):
        self.selected_value = ""
        self.selected_Id = 0