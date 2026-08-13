from app.cmn.resource_helper import PathManager
from app.cmn.AppName import *
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from kivy.config import Config

Config.set("graphics", "width", str(APP_WIDTH))
Config.set("graphics", "height", str(APP_HEIGHT))
Config.set("graphics", "resizable", "1")
Config.set("graphics", "borderless", "0")
Config.set('kivy', 'window_icon', str(PathManager.app_path("assets", "images", "icon.png")))

from app.Screens.HomeScreen import HomeScreen
from app.cmn.config_reader import ConfigReader
from app.cmn.font_manage import FontManager
from app.cmn.window_manager import WindowManager

from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window

class FlashCardApp (MDApp):
    title_icon = ""
    title_text = APP_NAME
    title = title_text
    _is_maximized = False

    def __init__(self, splash=None , **kwargs):
        super().__init__(**kwargs)
        self.splash = splash
        self.title_icon = str(PathManager.app_path("assets", "images", "icon.ico"))
        self.title_text = ConfigReader().get("App_Name")

    def build(self):
        FontManager.register_fonts()
        self.theme_cls.primary_palette = "Teal"
        FontManager.apply_kivymd_default_font(self.theme_cls)
        from widgets.CustomTitleBar import CustomTitleBar
        Builder.load_file(PathManager.app_path("Kv/HomeScreen.kv").__str__())
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="HomeScreen"))
        sm.current = "HomeScreen"
        return sm

    def close_app(self):
        Window.close()

    def toggle_maximize(self):
        if WindowManager.is_maximized():
            WindowManager.restore()
        else:
            WindowManager.maximize()

    def minimize_window(self):
        Window.minimize()
        
    def on_start(self):
        Clock.schedule_once(self._init_window, 0.3)
        WindowManager.set_window_icon(str(PathManager.app_path("assets", "images", "icon.ico")))
        Clock.schedule_once(self.close_splash, 20)

    def _init_window(self, dt):
        WindowManager.initialize()

    def close_splash(self, dt):
        self.splash.close()