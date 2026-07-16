from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.core.text import LabelBase
from widgets.MDLabelA import MDLabelA
from kivy.properties import StringProperty , BooleanProperty , NumericProperty
from kivymd.uix.bottomnavigation import  MDBottomNavigation , MDBottomNavigationItem 
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock

from Screens import *
from widgets.MDBottomNavigationItemA import MDBottomNavigationItemA
from cmn.logger import logger

class HomeScreen(MDScreen):
    def on_tab_switch(self, bottom_navigation, tab, tab_item):
        try:
            if len(tab.children) > 0:
                screen = tab.children[0]
                if hasattr(screen, 'on_tab_activated'):
                    self.on_tab_activated(screen=screen)
                    screen.on_tab_activated()
        except Exception as e:
            logger.info(f"❌ Eror: {e}")
    
    def on_tab_activated(self , screen):
        logger.info("open tab "+ screen.name)
        screen.on_tab_activated()
