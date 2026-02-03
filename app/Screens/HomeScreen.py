from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.core.text import LabelBase
from widgets.MDLabelA import MDLabelA
from kivy.properties import StringProperty , BooleanProperty , NumericProperty
from kivymd.uix.bottomnavigation import  MDBottomNavigation , MDBottomNavigationItem 
from kivymd.uix.screen import MDScreen
from Screens import *
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp


class HomeScreen(MDScreen):
    pass

class BaseMDNavigationItem(MDBottomNavigationItem):
    icon = StringProperty()
    text = StringProperty()
    badge_text = StringProperty()
    show_badge = BooleanProperty(False)
    screen_Name = StringProperty()
