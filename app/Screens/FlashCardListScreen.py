from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from cmn.resource_helper import *
from widgets.MDLabelA import MDLabelA
from widgets.MDCardA import MDCardA
from BL.FlashCardBL import FlashCardBL , OrderByConfig

Builder.load_file(resource_path("app/kv/FlashCardListScreen.kv"))

class FlashCardListScreen(MDScreen):
    def on_kv_post(self, base_widget):
        order_config = [OrderByConfig(field = 'id' , direction='desc')]
        self.load_flashcard(order_config)
        
    def load_flashcard(self , order_config):
        flashcardList = FlashCardBL().get_cards(order_config=order_config)
        
        self.ids.RV.data = [
        {       
            'title': flashcard.title or "",
            'example': flashcard.example or "",
            'collocation': flashcard.collocation or "",
            'pronunciation': flashcard.pronunciation or "",
            'partOfSpeach': getattr(flashcard.pos, 'caption', 'N/A'),
            'type_': getattr(flashcard.type_, 'caption', 'N/A'),
            'box': getattr(flashcard.box, 'caption', 'N/A'),
            'level': getattr(flashcard.level, 'caption', 'N/A')
        }
        for flashcard in flashcardList
    ]

