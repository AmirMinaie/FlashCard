from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from BL.FlashCardBL import *
from kivy.lang import Builder
from cmn.resource_helper import *

Builder.load_file(resource_path("app","kv/FlashCard.kv"))

class FlashCard(Screen):
    question_text = StringProperty("Loading question...")
    answer_text = StringProperty("Loading answer...")

    def on_pre_enter(self):
        self.flashcard = FlashCardBL()
        #self.flashcard.add_card("Amir","Minaie")
        #self.flashcard.add_card("Misam","Minaie")
        self.cards = self.flashcard.get_cards()
        self.index = 0
        self.show_current_card()

    def show_current_card(self):
        if not self.cards:
            self.question_text = "No cards available"
            self.answer_text = ""
            return

        card = self.cards[self.index]
        self.question_text = ""
        self.answer_text = ""

    def next_card(self):
        if not self.cards:
            return
        self.index = (self.index + 1) % len(self.cards)
        self.show_current_card()

    def add_new_card(self, question, answer):
        
        self.cards = self.flashcard.get_cards()