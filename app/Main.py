import sys
import os
from cmn.resource_helper import PathManager
from cmn.splash_screen import SplashScreen
APP_WIDTH = 736
APP_HEIGHT = 685

splash = SplashScreen(
    str(PathManager.app_path("assets", "images", "splash.bmp")),
    width= APP_WIDTH,
    height=APP_HEIGHT
)
splash.show()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from kivy.config import Config

Config.set("graphics", "width", str(APP_WIDTH))
Config.set("graphics", "height", str(APP_HEIGHT))
Config.set("graphics", "resizable", "0")
Config.set("graphics", "borderless", "0")

from Screens.HomeScreen import HomeScreen
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.lang import Builder
from cmn.config_reader import ConfigReader
from cmn.font_manage import FontManager
from kivy.clock import Clock
from cmn.backup_db import backup_database

class FlashCardApp (MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        FontManager.register_fonts()
        self.theme_cls.primary_palette = "Teal"
        FontManager.apply_kivymd_default_font(self.theme_cls)
        Builder.load_file(PathManager.app_path("Kv/HomeScreen.kv").__str__())
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="HomeScreen"))
        sm.current = "HomeScreen"
        return sm

    def on_start(self):
        # اجازه می‌دهد اولین فریم رابط کاربری ساخته شود
        Clock.schedule_once(
            self.close_splash,
            1,
        )

    def close_splash(self, dt):
        splash.close()
    
    def show_message(self, message, msg_type="info", duration=3):
        from widgets.SnackbarManager import snackbar_manager
        return snackbar_manager.show_snackbar(
            message=message,
            msg_type=msg_type,
            duration=duration
        )

def get_constant(name):
    try:
        from BL.constantBL import constantBL
        if name:
            name = str(name).lower().replace(' ','_')
            constant_bl = constantBL()
            constant = constant_bl.get_constant_name(name=name)
            constant_id = constant.id
            return constant_id
        else:
            return None
    
    except Exception as e:
        print (f" Error Load constant {name}: {e}")
        return 0

def LoadOldData():
    old_data_path = PathManager.CONFIG_DIR / "OldData.json"
    if not old_data_path.exists():
        return

    from BL.FlashCardBL import FlashCardBL
    data = ConfigReader("OldData.json").get('flashcards')
    loadOldData = ConfigReader("config.json").get("loadOldData" , 1 )
    flashcard_bl = FlashCardBL()
    
    if loadOldData == 1:
        for row in data:
            try:
                card = flashcard_bl.add_card(
                      title = row.get('title',None)
                     ,definition = row.get('definition',None)
                     ,example = row.get('example',None)
                     ,collocation = row.get('collocation',None)
                     ,pastParticiple = row.get('pastParticiple',None)
                     ,pastTense = row.get('pastTense',None)
                     ,pronunciation = row.get('pronunciation',None)
                     ,pos_id = get_constant(row.get('pos',None))
                     ,type_id = get_constant(row.get('type',None))
                     ,box_id = get_constant(row.get('box',None))
                     ,level_id = get_constant(row.get('level',None))
                     ,notion_content = row.get('notion_content',None)
                     ,files = [
                         {
                            "value" : file.get('value',None) , 
                            "from_type_id": get_constant(file.get('from_type_caption',None)) 
                          } for file in row.get('fileFlashcard',None)]
                     ,createAt = row.get('createdAt',None)
                     ,updatedAt = row.get('updatedAt',None)
                     ,reviews = row.get('reviewFlashcard',None)
                )
                print(f"insert row {row.get('title',None)}: {card['id']}")
            except Exception as e:
                print(f"Errro insert row {row.get('title',None)}: {e}")
        
        ConfigReader("config.json").set("loadOldData" , 0 )

if __name__ == "__main__":
    print("Starting FlashCard Application...")
    try:
        backup_database()
        from DA import init_db
        init_db()
        LoadOldData()

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

    FlashCardApp().run()