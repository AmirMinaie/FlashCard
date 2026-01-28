from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from BL.FlashCardBL import FlashCardBL
from kivy.lang import Builder
from cmn.resource_helper import *

Builder.load_file(resource_path("app","Kv/FlashCardAdd.kv"))

class FlashCardAdd(MDScreen):

    def add_card(self, close_after=False):
        title = self.ids.title_field.text.strip()
        type_ = self.ids.type_field.text.strip()
        description = self.ids.description_field.text.strip()
        example = self.ids.example_field.text.strip()
        voice = self.ids.voice_field.text.strip()

        if not title or not type_:
            MDDialog(
                title="Error",
                text="Title and Type are required!",
                size_hint=(0.8, None)
            ).open()
            return

        bl = FlashCardBL()
        cardId= bl.add_card(
            title=title,
            type_Id=type_,
            description=description,
            example=example,
        )
        

        MDDialog(
            title="Success",
            text=f"Flashcard {cardId} added successfully!",
            size_hint=(0.8, None)
        ).open()

        self.ids.title_field.text = ""
        self.ids.type_field.text = ""
        self.ids.description_field.text = ""
        self.ids.example_field.text = ""
        self.ids.voice_field.text = ""

        if close_after:
            self.manager.current = "Menu"
