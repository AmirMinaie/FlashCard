from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from Screens import *
from DA import init_db
from DA.seed import seed
import importlib
import inspect
from kivy.uix.screenmanager import Screen
from kivymd.uix.screen import MDScreen

class MyScreenManager(ScreenManager):
    pass

class FlashCardApp(MDApp):
    def build(self):
        init_db()
        seed()
        sm = MyScreenManager()
        add_all_screens(sm)
        sm.current = 'HomeScreen'
        return sm
    
    def go_home(self):
        self.root.current = "HomeScreen"
    
    def go_menu(self):
        self.root.current = "Menu"

def add_all_screens(sm):
    import Screens
    for name, obj in inspect.getmembers(Screens):
        if inspect.isclass(obj) and ( issubclass(obj, Screen) or issubclass(obj, MDScreen)) and obj not in ( MDScreen , Screen): 
            screen_instance = obj(name=obj.__name__)
            sm.add_widget(screen_instance)
