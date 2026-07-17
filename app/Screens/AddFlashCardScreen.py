from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from cmn.resource_helper import *
from widgets.MDLabelA import MDLabelA
from widgets.MDTextFieldA import MDTextFieldA
from widgets.DropDownA import DropDownA
from BL.constantBL import constantBL
from BL.FlashCardBL import FlashCardBL
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.button import MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from widgets.BaseButtonA import BaseButtonA
from kivy.core.audio import SoundLoader
from cmn.resource_helper import PathManager
from urllib.parse import urlparse, unquote
from os.path import basename
from cmn.logger import logger
from widgets.AsyncButton import AsyncButton
from itertools import zip_longest
from widgets.SnackbarManager import snackbar_manager , Msg_type

import uuid
from kivy.properties import StringProperty, NumericProperty, DictProperty, BooleanProperty , ObjectProperty 


Builder.load_file(str(PathManager.app_path( "Kv/AddFlashCardScreen.kv")))

class AddFlashCardScreen(MDScreen):
    form_title = StringProperty("Add New FlashCard")
    save_button_text = StringProperty("Save FlashCard")

    mode = StringProperty("add")
    card_id = NumericProperty(-1)

    def update_form_mode_ui(self):
        if self.mode == "add":
            self.form_title = "Add New FlashCard"
            self.save_button_text = "Save FlashCard"

        elif self.mode == "edit":
            self.form_title = f"Edit FlashCard {self.card_id}"
            self.save_button_text = "Update FlashCard"

    def set_card_id(self, card_id):
        self.card_id = card_id
        self.mode = "edit"
        self.update_form_mode_ui()

        flashCardBL = FlashCardBL()
        card = flashCardBL.get_card_by_id(card_id)

        if not card:
            return

        self.ids.title_field.text = card.title or ""
        self.ids.definition_field.text = card.definition or ""
        self.ids.example_field.text = card.example or ""
        self.ids.collocation_field.text = card.collocation or ""

        self.ids.pastParticiple_field.text = card.pastParticiple or ""
        self.ids.pastTense_field.text = card.pastTense or ""
        self.ids.pronunciation_field.text = card.pronunciation or ""

        self.ids.part_of_speech_field.set_selected_by_id(card.pos_id)
        self.ids.type_field.set_selected_by_id(card.type_id)
        self.ids.box_field.set_selected_by_id(card.box_id)

        if card.level_id:
            self.ids.level_field.set_selected_by_id(card.level_id)  
        self.ids.songs_playlist.clear()
        for file in card.files:
            item = {
                "id": file.id,
                "title":file.title,
                "fileName": file.fileName,
                "value": file.filePath,
                "from_type_id": file.sourceType_id,
                "from_type_caption": file.sourceType.caption
            }
            self.ids.songs_playlist.add_song(item)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialog_add_song = None
        self.add_card = []
        self.player = None

    def load_constant(self , type):
        constant_pos = constantBL().get_constant(type)
        data = [{"caption":pos.caption, "id" :  pos.id } for pos in constant_pos]
        return data

    def befor_Save_info(self):

        validation_result = self.validate_form()
        self.ids.songs_playlist.stop_player()
        if not validation_result["is_valid"]:
            snackbar_manager.show_snackbar( message=validation_result["message"], msg_type=Msg_type.error )
            return False
        return True
    
    def Save_info(self):
        try:
            data = self.collect_form_data()

            flashCardBL = FlashCardBL()

            if self.mode == "edit" and self.card_id > 0:
                saved_card = flashCardBL.update_card(self.card_id , **data)
            else:
                saved_card = flashCardBL.add_card(**data)
            
            return  saved_card

        except ValueError as e:
            
            self.show_validation_error(str(e))

        except Exception as e:
            self.show_generic_error(str(e))
    
    def handle_save_error(self , e):
        if isinstance(e, ValueError):
            self.show_validation_error(str(e))
        else:
            self.show_generic_error(str(e))

    def After_Save_info(self , result):
        try:
            saved_card = result 
            if saved_card and saved_card['id']:
                self.show_success_message(saved_card)
                self.reset_form()

            else:
                self.show_save_failed_message()
                
        except Exception as e:
            self.show_generic_error(str(e))

    def cancel_edit(self):
        self.reset_form()

    def validate_form(self):
        errors = []
        warnings = []

        required_text_fields = [
            ('title_field', 'Word/Title'),
            ('definition_field', 'Definition'),
            ('example_field', 'Example Sentence'),
        ]

        for field_id, field_name in required_text_fields:
            field = self.ids.get(field_id)
            if field and (not field.text or not field.text.strip()):
                errors.append(field_name)
                if hasattr(field, 'error'):
                    field.error = True
                    field.helper_text = f"{field_name} is required!"

        required_dropdowns = [
            ('part_of_speech_field', 'Part of Speech'),
            ('type_field', 'Type'),
            ('level_field', 'Level'),
            ('box_field', 'Box'),
        ]

        for field_id, field_name in required_dropdowns:
            field = self.ids.get(field_id)
            if field and field.is_required and not field.selected_value:
                errors.append(field_name)

        if self.ids.title_field.text.strip() and len(self.ids.title_field.text.strip()) < 2:
            warnings.append("Word/Title is too short")

        if self.ids.definition_field.text.strip() and len(self.ids.definition_field.text.strip()) < 10:
            warnings.append("Definition is too short")

        if errors:
            return {
                "is_valid": False,
                "message": f"Required fields: {', '.join(errors)}",
                "errors": errors,
                "warnings": warnings
            }

        if warnings:
            return {
                "is_valid": True,
                "message": f"Warnings: {', '.join(warnings)}",
                "errors": [],
                "warnings": warnings
            }

        return {
            "is_valid": True,
            "message": "Form is valid",
            "errors": [],
            "warnings": []
        }

    def collect_form_data(self):
        return {
            'title': self.ids.title_field.text.strip(),
            'definition': self.ids.definition_field.text.strip(),
            'example': self.ids.example_field.text.strip(),
            'collocation': self.ids.collocation_field.text.strip(),
            'pastParticiple': self.ids.pastParticiple_field.text.strip() if hasattr(self.ids, 'pastParticiple_field') else "",
            'pastTense': self.ids.pastTense_field.text.strip() if hasattr(self.ids, 'pastTense_field') else "",
            'pronunciation': self.ids.pronunciation_field.text.strip() if hasattr(self.ids, 'pronunciation_field') else "",
            'pos_id': self.ids.part_of_speech_field.selected_Id or 0,
            'type_id': self.ids.type_field.selected_Id or 0,
            'box_id': self.ids.box_field.selected_Id or 0,
            'level_id': self.ids.level_field.selected_Id or 0,
            'files': self.ids.songs_playlist.songs,
        }

    def show_success_message(self, saved_card):
        message = f"saved successfully!\n"
        message +=f"Title: {saved_card['title']} ID: #{saved_card['id']}"
        snackbar_manager.show_snackbar( message=message, msg_type=Msg_type.success )
        
    def show_validation_error(self, error_message):
        snackbar_manager.show_snackbar( message=f"Validation Error: {error_message}", msg_type=Msg_type.error )

    def show_database_error(self, error_message):
        snackbar_manager.show_snackbar( message="Database Error. Please try again.", msg_type=Msg_type.error )
        logger.info(f"Database Error: {error_message}")

    def show_generic_error(self, error_message):
        snackbar_manager.show_snackbar( message=f"An unexpected error occurred {error_message}", msg_type=Msg_type.error )
        logger.info(f"Error: {error_message}")

    def show_save_failed_message(self):
        snackbar_manager.show_snackbar( message="Failed to save flash card. Please check your data and try again.", msg_type=Msg_type.warning )

    def show_add_song_dialog(self):

        if not self.dialog_add_song:

            self.song_dialog_content = Builder.load_string("""
MDBoxLayout:
    orientation: "vertical"
    spacing: dp(15)
    padding: dp(15)
    size_hint_y: None
    height: dp(310)

    MDSeparator:
        height: dp(1)


    DropDownA:
        id: source_field
        text_h: "Source Type"
        icon: "source-branch"
        selected_value: ""
        is_required: True
        size_hint_y: None
        height: dp(55)

    TextInput:
        id: song_title_field
        text_h: "Title"
        hint_text: "Enter a title for this song"
        icon: "format-title"
        mode: "rectangle"
        multiline: True
        size_hint_y: None
        height: dp(100)
                                                                  
    TextInput:
        id: song_path_fields
        text_h: "Song URL / File Path"
        hint_text: "Enter song URL or local file path"
        icon: "music-note"
        mode: "rectangle"
        multiline: True
        size_hint_y: None
        height: dp(100)
""")

            self.song_dialog_content.ids.source_field.item_menu = self.load_constant('source_type')
            self.dialog_add_song = MDDialog(
                title="Add New Song",
                type="custom",
                content_cls=self.song_dialog_content,
                buttons=[
                    BaseButtonA( text="CANCEL", icon="close",
                        on_release=self.close_dialog_add_song),
                    BaseButtonA( text="ADD", icon="plus",
                        on_release=self.add_new_song_item),
                ]
            )

        self.song_dialog_content.ids.song_path_fields.text = ""
        self.song_dialog_content.ids.song_title_field.text = ""
        self.song_dialog_content.ids.source_field.clear_selection()
        self.dialog_add_song.open()

    def close_dialog_add_song(self , *args):
        """Close the dialog"""
        if self.dialog_add_song:
            self.dialog_add_song.dismiss()

    def add_new_song_item(self, *args):
    
        source = self.song_dialog_content.ids.source_field
        path = self.song_dialog_content.ids.song_path_fields
        title = self.song_dialog_content.ids.song_title_field

        paths = [p.strip() for p in path.text.splitlines() if p.strip()]
        titles = [t.strip() for t in title.text.splitlines()]

        for title_text, path_text in zip_longest(titles, paths, fillvalue=""):
            if not path_text:
                continue
            
            item = {
                "title": title_text,
                "from_type_id": source.selected_Id,
                "fileName": unquote(basename(urlparse(path_text).path)),
                "from_type_caption": source.selected_value,
                "value": path_text,
            }

            self.ids.songs_playlist.add_song(item)
    
        self.close_dialog_add_song()
        
    def reset_form(self):
        self.card_id = -1
        self.mode = "add"
        self.update_form_mode_ui()
        text_fields = [
            'title_field', 'definition_field', 'example_field', 
            'collocation_field', 'pastParticiple_field', 
            'pastTense_field', 'pronunciation_field'
        ]

        for field_id in text_fields:
            field = self.ids.get(field_id)
            if field:
                field.text = ""
                if hasattr(field, 'error'):
                    field.error = False
                    field.helper_text = ""

        dropdowns = [
            'part_of_speech_field', 'type_field', 
            'level_field', 'box_field'
        ]

        for field_id in dropdowns:
            field = self.ids.get(field_id)
            if field and hasattr(field, 'clear_selection'):
                field.clear_selection()
        
        self.song_list = []
        self.ids.songs_playlist.clear()

    def befor_delete(self):
        return self.card_id > 0
    
    def After_delete(self , result):
        snackbar_manager.show_snackbar( message="Flash card deleted successfully", msg_type=Msg_type.success )
        self.reset_form()

    def handle_delete(self , e):
        logger.error(str(e))
        self.show_generic_error("Delete failed")

    def delete_card(self):
        flashCardBL = FlashCardBL()
        result = flashCardBL.delete_card(self.card_id)
        return result