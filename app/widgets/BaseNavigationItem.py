# BaseNavigationItem.py
from kivymd.uix.navigationbar import MDNavigationItem
from kivy.properties import StringProperty

class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()
