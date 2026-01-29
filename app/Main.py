from Screens.HomeScreen import HomeScreen
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from cmn.resource_helper import resource_path
from kivy.lang import Builder
from them import register_fonts
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class FlashCardApp (MDApp):
    def build(self):
        register_fonts(self.theme_cls)
        Builder.load_file(resource_path("app/kv/HomeScreen.kv"))

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="HomeScreen"))
        sm.current = "HomeScreen"
        return sm


if __name__ == "__main__":
    print("Starting FlashCard Application...")
    try:
        from DA import init_db
        init_db()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

    FlashCardApp().run()
