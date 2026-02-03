from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from cmn.resource_helper import *
from widgets.MDLabelA import MDLabelA
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from BL.constantBL import constantBL
from widgets.DropDownA import DropDownA
from BL.FlashCardBL import FlashCardBL
from kivymd.app import MDApp

Builder.load_file(resource_path("app/kv/AddFlashCardScreen.kv"))

class AddFlashCardScreen(MDScreen):
    
    def load_constant(self , type):
        constant_pos = constantBL().get_constant(type)
        data = [{"caption":pos.caption, "id" :  pos.id } for pos in constant_pos]
        return data

    def show_menu_pos(self , instans):
        return self.load_constant('POS')

    def show_menu_type(self , instans):
        return self.load_constant('FlashCardtype')

    def show_menu_level(self , instans):
        return self.load_constant('Level')
    
    def show_menu_box(self , instans):
        return self.load_constant('Box')

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