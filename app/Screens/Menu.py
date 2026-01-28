from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivymd.uix.list import MDListItem
from kivymd.uix.button import MDIconButton
from kivy.lang import Builder
from cmn.resource_helper import *

Builder.load_file(resource_path("app","kv/Menu.kv"))

class Menu(MDScreen):

    def on_pre_enter(self):
        Clock.schedule_once(self.load_menu)

    def load_menu(self, dt):

        container = self.ids.menu_list
        container.clear_widgets()

        for item in self.get_menu_items():
            list_item = OneLineIconListItem(
                text=item["title"],
                on_release=lambda x, screen=item["screen"]: self.go_to(screen)
            )
            list_item.add_widget(
                IconLeftWidget(icon=item.get("icon", "chevron-right"))
            )
            container.add_widget(list_item)

    def go_to(self, screen_name):
        self.manager.current = screen_name

    def get_menu_items(self):
        return [
            {"title": "Review", "screen": "flashcard_Review", "icon": "calendar-today"},
            {"title": "Add", "screen": "FlashCardAdd", "icon": "card-plus-outline"},
            {"title": "All", "screen": "flashcard_all", "icon": "cards"}
        ]