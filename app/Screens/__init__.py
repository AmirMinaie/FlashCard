import os
import importlib
from cmn.resource_helper import *
from kivy.uix.screenmanager import Screen
from kivymd.uix.screen import MDScreen

__all__ = []

screen_dir = resource_path("Screens" )
for file in os.listdir(screen_dir):
    if file.endswith(".py") and file != "__init__.py":
        screen_name = f"{__name__}.{file[:-3]}"
        screen = importlib.import_module(screen_name)

        for attr_name in dir(screen):
            attr = getattr(screen, attr_name)
            try:
                if isinstance(attr, type) and ( issubclass(attr, Screen) or issubclass(attr, MDScreen)) and attr not in ( MDScreen , Screen):
                    globals()[attr_name] = attr
                    __all__.append(attr_name)
            except TypeError:
                pass

print("screen loaded dynamically:", __all__)
