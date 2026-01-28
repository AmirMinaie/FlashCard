from Screens.HomeScreen import HomeScreen
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from cmn.resource_helper import resource_path
from kivy.lang import Builder
from them import register_fonts

class FlashCardApp (MDApp):
    def build(self):
        register_fonts(self.theme_cls)
        Builder.load_file(resource_path("kv/HomeScreen.kv"))

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="HomeScreen"))
        sm.current = "HomeScreen"
        return sm


if __name__ == "__main__":
    FlashCardApp().run()
