from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from cmn.resource_helper import *
from widgets.MDLabelA import MDLabelA
from widgets.MDCardA import MDCardA
from BL.FlashCardBL import FlashCardBL

Builder.load_file(resource_path("app/kv/FlashCardListScreen.kv"))

class FlashCardListScreen(MDScreen):
    def on_kv_post(self, base_widget):
        flashcardList = FlashCardBL().get_cards()
        grid = self.ids.grid

        for flashcard in flashcardList:
            card = MDCardA(
                    title= flashcard.title,
                    example= flashcard.example ,
                    collocation= flashcard.collocation ,
                    pronunciation= flashcard.pronunciation ,
                    partOfSpeach= flashcard.pos.caption ,
                    type_= flashcard.type_.caption ,
                    box= flashcard.box.caption ,
                    level= flashcard.level.caption ,
                )
            
            grid.add_widget(card)
    
    pass
