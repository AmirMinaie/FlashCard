from Screens.HomeScreen import HomeScreen
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from cmn.resource_helper import resource_path
from kivy.lang import Builder
from kivy.properties import ListProperty
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class FlashCardApp (MDApp):
    #custom_primary_color = ListProperty([0.12, 0.56, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        Builder.load_file(resource_path("app/kv/HomeScreen.kv"))
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="HomeScreen"))
        sm.current = "HomeScreen"
        return sm

    def on_start(self):
        from kivy.core.text import LabelBase
        return super().on_start()
    
    def show_message(self, message, msg_type="info", duration=3):
        from widgets.SnackbarManager import snackbar_manager
        return snackbar_manager.show_snackbar(
            message=message,
            msg_type=msg_type,
            duration=duration
        )

if __name__ == "__main__":
    print("Starting FlashCard Application...")
    try:
        from DA import init_db
        init_db()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

    FlashCardApp().run()
