from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from cmn.resource_helper import *
from widgets.MDLabelA import MDLabelA
from widgets.MDTextFieldA import MDTextFieldA
from widgets.DropDownA import DropDownA
from BL.constantBL import constantBL
from BL.FlashCardBL import FlashCardBL
from BL.fileManager import FileManager
from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.button import MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivy.core.audio import SoundLoader
from cmn.resource_helper import PathManager
from urllib.parse import urlparse, unquote
from os.path import basename

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

        self.song_list = []
        self.ids.song_list.clear_widgets() 

        for file in card.files:
            item = {
                "id": file.id,
                "fileName": file.fileName,
                "value": file.filePath,
                "from_type_id": file.sourceType_id,
                "from_type_caption": file.sourceType.caption
            }

            self.add_List_song(item)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialog_add_song = None
        self.add_card = []
        self.player = None
        self.song_list = []
    
    def on_tab_activated(self):
        print("open Add Screen")

    def load_constant(self , type):
        constant_pos = constantBL().get_constant(type)
        data = [{"caption":pos.caption, "id" :  pos.id } for pos in constant_pos]
        return data

    def Save_info(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        validation_result = self.validate_form()
        if not validation_result["is_valid"]:
            app.show_message(
                message = validation_result["message"],
                msg_type ="error",
                duration =5
            )
            return

        try:
            data = self.collect_form_data()

            flashCardBL = FlashCardBL()

            if self.mode == "edit" and self.card_id > 0:
                saved_card = flashCardBL.update_card(self.card_id , **data)
            else:
                saved_card = flashCardBL.add_card(**data)

            if saved_card and saved_card['id']:
                self.show_success_message(saved_card)
                self.reset_form()

            else:
                self.show_save_failed_message()

        except ValueError as e:
            self.show_validation_error(str(e))

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
            'files': self.song_list,
        }

    def show_success_message(self, saved_card):
        app = MDApp.get_running_app()

        message = f"""
Flash card saved successfully!
Title: {saved_card['title']}
ID: #{saved_card['id']}
        """

        app.show_message(
            message,
            msg_type="success",
            duration=4
        )

    def show_validation_error(self, error_message):
        app = MDApp.get_running_app()
        app.show_message(
            f"Validation Error: {error_message}",
            msg_type="error",
            duration=5
        )

    def show_database_error(self, error_message):
        """نمایش خطای دیتابیس"""
        app = MDApp.get_running_app()
        app.show_message(
            "Database Error. Please try again.",
            msg_type="error",
            duration=5
        )
        # لاگ کردن خطا برای دیباگ
        print(f"Database Error: {error_message}")

    def show_generic_error(self, error_message):
        """نمایش خطای عمومی"""
        app = MDApp.get_running_app()
        app.show_message(
            "An unexpected error occurred.",
            msg_type="error",
            duration=5
        )
        print(f"Error: {error_message}")

    def show_save_failed_message(self):
        """نمایش پیام عدم موفقیت در ذخیره"""
        app = MDApp.get_running_app()
        app.show_message(
            "Failed to save flash card. Please check your data and try again.",
            msg_type="warning",
            duration=5
        )

    def show_add_song_dialog(self):
        """Show dialog for adding new item"""
        if not self.dialog_add_song:
            # Create content layout
            content = MDBoxLayout(
                orientation="vertical",
                spacing="12dp",
                size_hint_y=None,
                height="120dp"
            )
            
            # add file from DropDown
            self.from_DropDown_field = DropDownA(
                    text_h = "from",
                    selected_value = "",
                    is_required = True,
                    item_menu = self.load_constant('source_type')
                    )
            
            content.add_widget(self.from_DropDown_field)

            # Text field for item name
            self.value_field = MDTextFieldA(
                hint_text="value",
                mode="rectangle",
                size_hint_x=None,
                width="300dp"
            )
            content.add_widget(self.value_field)
            
            # Create dialog
            self.dialog_add_song = MDDialog(
                title="Add New Item",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.close_dialog_add_song
                    ),
                    MDFlatButton(
                        text="ADD",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.add_new_song_item
                    ),
                ],
            )
        
        # Clear text field and open dialog
        self.value_field.text = ""
        self.from_DropDown_field.clear_selection()
        self.dialog_add_song.open()
    
    def close_dialog_add_song(self , *args):
        """Close the dialog"""
        if self.dialog_add_song:
            self.dialog_add_song.dismiss()

    def add_new_song_item(self , *args):
        item={
                "from_type_id": self.from_DropDown_field.selected_Id,
                "fileName": unquote(basename(urlparse( self.value_field.text).path)) ,
                "from_type_caption": self.from_DropDown_field.selected_value,
                "value":self.value_field.text
            }
        self.add_List_song(item)
        self.close_dialog_add_song()
        pass

    def add_List_song(self, item):
        """Add a song item to the list"""
        if 'id' not in item:
            item['id'] = f"new_{uuid.uuid4()}"

        self.song_list.append(item)

        list_item = OneLineIconListItem(
            text=f"{item['fileName']} ({item['from_type_caption']})"
        )
        list_item.item_data = item

        delete_btn = MDIconButton(
            icon="delete",
            pos_hint={"center_y": 0.5},
            theme_text_color="Error"
        )

        delete_btn.bind(on_release=self.delete_song_item)            
        list_item.bind(on_release=lambda x: self.play_song_item(list_item))
        list_item.add_widget(delete_btn)
        self.ids.song_list.add_widget(list_item)

    def delete_song_item(self ,instance):
        """حذف آیتم"""
        instance.disabled = True
        parent = instance.parent
        if parent:
        
            item_to_delete = parent.item_data
            self.song_list = [song for song in self.song_list 
                                if song.get('id') != item_to_delete.get('id')]

            self.ids.song_list.remove_widget(parent)
            self.ids.song_list.height = self.ids.song_list.minimum_height

        return True

    def play_song_item(self, instance):
        item_data = instance.item_data
    
        # اگر صدای قبلی در حال پخش است، متوقفش کن
        if hasattr(self, "sound") and self.sound is not None:
            try:
                self.sound.stop()
            except Exception as e:
                print("STOP SOUND ERROR:", e)
            finally:
                self.sound = None
    
        try:
            if isinstance(item_data["id"], int):
                file_path = FileManager.getfilepath(item_data["value"])
            else:
                file_path =  item_data["value"]
    
            print("PLAY:", file_path)
    
            # فایل صوتی را لود کن
            self.sound = SoundLoader.load(file_path)
    
            if self.sound is None:
                raise Exception(f"Audio file could not be loaded: {file_path}")
    
            # تنظیمات صدا
            self.sound.volume = 1.0
            self.sound.loop = False
    
            # پخش
            self.sound.play()
    
        except Exception as e:
            print("PLAY SOUND ERROR:", e)
            self.sound = None
            self.show_generic_error(e)

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
        self.ids.song_list.clear_widgets()

    def confirm_delete(self):
        if self.card_id <= 0:
            return
    
        self.delete_dialog = MDDialog(
            title="Delete FlashCard",
            text="Are you sure you want to delete this flash card?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.delete_dialog.dismiss()
                ),
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x: self.delete_card()
                )
            ]
        )
    
        self.delete_dialog.open()

    def delete_card(self):
        flashCardBL = FlashCardBL()

        result = flashCardBL.delete_card(self.card_id)

        self.delete_dialog.dismiss()

        if result:
            app = MDApp.get_running_app()

            app.show_message(
                "Flash card deleted successfully",
                msg_type="success",
                duration=4
            )

            self.reset_form()
        else:
            self.show_generic_error("Delete failed")
