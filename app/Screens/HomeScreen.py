from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from cmn.resource_helper import *

Builder.load_file(resource_path("app","kv/HomeScreen.kv"))

class HomeScreen(Screen):
    pass
