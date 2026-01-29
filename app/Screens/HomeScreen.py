from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.core.text import LabelBase
from them import register_fonts
from widgets.MDLabelA import MDLabelA
from kivy.properties import StringProperty , BooleanProperty , NumericProperty
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.screen import MDScreen
from Screens import *


class HomeScreen(MDScreen):

    def on_switch_tabs(
        self,
        bar: MDNavigationBar,
        item: MDNavigationItem,
        item_icon: str,
        item_text: str, 
        ):

        self.ids.screen_manager.current = item.screen_Name
        item.show_badge = True
        item.badge_text = "10"

class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()
    badge_text = StringProperty()
    show_badge = BooleanProperty(False)
    screen_Name = StringProperty()
