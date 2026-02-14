from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from cmn.resource_helper import *
from widgets.MDLabelA import MDLabelA
from widgets.DropDownA import DropDownA
from BL.constantBL import constantBL
from BL.FlashCardBL import FlashCardBL
from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.button import MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from ffpyplayer.player import MediaPlayer
from kivy.properties import StringProperty, NumericProperty, DictProperty, BooleanProperty , ObjectProperty 
import time

Builder.load_file(resource_path("app/Kv/AddFlashCardScreen.kv"))

class AddFlashCardScreen(MDScreen):
    mode = StringProperty("add")
    card_id = NumericProperty(-1)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialog_add_song = None
        self.add_card = []
        self.player = None
        self.song_list = []
    
    def on_screen_current(self, instance, value):
        """وقتی current صفحه تغییر می‌کند"""
        if value == self.name:  # اگر این صفحه active شد
            print("✅ صفحه فعال شد")
            self.on_activate()


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
            self.value_field = MDTextField(
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
                "from_type_caption": self.from_DropDown_field.selected_value,
                "value":self.value_field.text
            }
        self.add_List_song(item)
        self.close_dialog_add_song()
        pass

    def add_List_song(self, item):
        """Add a song item to the list"""
        if 'id' not in item:
            item['id'] = len(self.song_list) + 1

        self.song_list.append(item)

        list_item = OneLineIconListItem(
            text=f"{item['value']} ({item['from_type_caption']})"
        )
        list_item.item_data = item

        delete_btn = MDIconButton(
            icon="delete",
            pos_hint={"center_y": 0.5},
            theme_text_color="Error"
        )

        delete_btn.bind(on_press=self.delete_song_item)            
        list_item.bind(on_release=lambda x: self.play_song_item(list_item))
        list_item.add_widget(delete_btn)
        self.ids.song_list.add_widget(list_item)

    def delete_song_item(self ,instance):
        """حذف آیتم"""
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
        if hasattr(self, 'player') and self.player is not None:
            try:
                self.player.set_pause(True)
                time.sleep(0.02)
                self.player.close()
                time.sleep(0.02)
            except:
                pass
            finally:
                self.player = None
        try:
            time.sleep(0.05)
            self.player = MediaPlayer(
            item_data['value'],
            ff_opts={
                'paused': False,
                'sync': 'audio',
                'buffer_size': '512000',
                'rtbufsize': '1024000',
                'infbuf': 1,
                'reconnect': 1,
                'reconnect_delay_max': 5
            }
        )
        
        except Exception as e:
            self.show_generic_error(e)

    def reset_form(self):
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