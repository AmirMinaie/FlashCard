from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from cmn.resource_helper import resource_path
from BL.FlashCardBL import FlashCardBL
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from widgets.MDChipA import MDChipA
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from datetime import datetime
from kivy.clock import Clock
from kivy.metrics import dp
from widgets.Playlist import Playlist

Builder.load_file(resource_path("app/Kv/ReviewScreen.kv"))

class ReviewScreen(MDScreen):
    show_answer = BooleanProperty(False)
    current_card = None
    total_today_reviews = NumericProperty(0)
    session_completed = BooleanProperty(False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flashcard_bl = FlashCardBL()
        self.current_card = None
        self.session_dialog = None
        self.no_more_cards_dialog = None
        self.parent_tab = None
    
    def on_parent(self, widget, parent):
        """وقتی صفحه به والد اضافه شد"""
        if parent:
            self.parent_tab = parent
    
    def update_badge_from_screen(self, count):
        """آپدیت بدج از داخل صفحه"""
        pass
    
    def on_kv_post(self, *args):
        """هر بار که وارد صفحه می‌شود"""
        self.show_answer = False
        self.session_completed = False
        self.total_today_reviews = self.flashcard_bl.get_today_reviewed_count()
        self.load_next_card()
    
    def load_next_card(self):
        """لود کارت بعدی از دیتابیس"""
        try:
            # توقف پخش صداهای قبلی
            self.stop_playlist()
            
            # مخفی کردن بخش‌های جواب
            self.hide_answer_fields()
            
            self.current_card = self.flashcard_bl.get_next_card_for_review()
            review_count = self.flashcard_bl.get_today_review_count()
            self.update_badge_from_screen(review_count)
            if self.current_card:
                
                # تنظیم دکمه‌ها
                self.ids.button_box.opacity = 1
                self.ids.button_box.disabled = False
                self.ids.answer_button_box.opacity = 0
                self.ids.answer_button_box.disabled = True
                self.session_completed = False
                
                self.ids.flashcard_box.opacity = 1
                self.ids.flashcard_box.disabled = False

                self.compleat_Session_Box.opacity = 0
                self.compleat_Session_Box.disabled = True
        
                
                # مقداردهی فیلدهای همیشه نمایش
                self.set_fields(True , False)
                
                self.update_counter()
                
            else:
                # اگر کارتی برای مرور نبود
                self.show_session_completed()
                
        except Exception as e:
            print(f"Error loading next card: {e}")
            self.show_error_message("Error loading card. Please try again.")
    
    def set_fields(self , show_always , default):
        """مقدار دهی فیلدهای همیشه نمایش"""
        for field in self.fields_config():
            if field['show_always'] == show_always:
                if default:
                    value = field['default']
                else:
                    value = self.get_card_attribute(field['card_attribute'], field['default'])
                self._set_widget_value(field['id'], field['attribute'], value)
    
    def show_answer_fields(self):
        """نمایش فیلدهای جواب"""
        if not self.current_card:
            return
            
        self.set_fields(show_always=False ,default=False)
        
        # تغییر دکمه‌ها
        self.ids.button_box.height = 0
        self.ids.button_box.opacity = 0
        self.ids.button_box.disabled = True

        self.ids.answer_button_box.height = 60
        self.ids.answer_button_box.opacity = 1
        self.ids.answer_button_box.disabled = False
        self.ids.button_area.height = 65
        
        self.show_answer = True
    
    def hide_answer_fields(self):
        # ریست کردن مقادیر
        self.set_fields(show_always=False ,default=True)
        
        # تغییر وضعیت دکمه‌ها
        if not self.session_completed:
            self.ids.button_box.opacity = 1
            self.ids.button_box.disabled = False
        
        # تغییر دکمه‌ها
        self.ids.button_box.height = 60
        self.ids.button_box.opacity = 1
        self.ids.button_box.disabled = False

        self.ids.answer_button_box.height = 0
        self.ids.answer_button_box.opacity = 0
        self.ids.answer_button_box.disabled = True
        self.ids.button_area.height = 65
        
        self.show_answer = False
    
    def get_card_attribute(self, attribute_path, default=""):
        """گرفتن مقدار از کارت با path داده شده"""
        if not self.current_card:
            return default
            
        try:
            attrs = attribute_path.split('.')
            value = self.current_card
            for attr in attrs:
                value = getattr(value, attr, None)
                if value is None:
                    return default
            return value if value is not None else default
        except Exception as e:
            print(f"Error getting attribute {attribute_path}: {e}")
            return default
    
    def setup_playlist(self):
        """تنظیم playlist برای صداهای کارت"""
        # این بخش بستگی به پیاده‌سازی Playlist شما دارد
        pass
    
    def mark_card_quality(self ,quality):
        """علامت‌گذاری کارت   """
        try:
            if self.current_card:
                success = self.flashcard_bl.mark_card_reviewed(
                    card_id=self.current_card.id,
                    quality_Answer=quality
                )
                
                if success:
                    self.show_success_indicator("✓ Correct")
                    self.total_today_reviews += 1
            
            # لود کارت بعدی
            Clock.schedule_once(lambda dt: self.load_next_card(), 0.5)
            
        except Exception as e:
            print(f"Error marking card correct: {e}")
            self.show_error_message("Error saving review. Please try again.")
            Clock.schedule_once(lambda dt: self.load_next_card(), 0.5)
 
    def skip_card(self):
        """رد کردن کارت فعلی"""
        try:
            if self.current_card:
                self.flashcard_bl.mark_card_reviewed(
                    card_id=self.current_card.id,
                    quality_Answer=-1
                )
                self.show_success_indicator("⏭ Skipped")
            
            # لود کارت بعدی
            Clock.schedule_once(lambda dt: self.load_next_card(), 0.5)
            
        except Exception as e:
            print(f"Error skipping card: {e}")
            self.load_next_card()
    
    def show_session_completed(self):
        """نمایش پیام پایان جلسه مرور"""
        self.session_completed = True
        
        # مخفی کردن دکمه‌ها
        self.ids.button_box.opacity = 0
        self.ids.button_box.disabled = True
        self.ids.answer_button_box.opacity = 0
        self.ids.answer_button_box.disabled = True
        
        self.ids.flashcard_box.opacity = 0
        self.ids.flashcard_box.disabled = True

        self.ids.compleat_Session_Box.opacity = 1
        self.ids.compleat_Session_Box.disabled = False
        
        # نمایش پیام در کارت
        
        self.ids.compleat_Session_lable.text = "Session Completed!\n"
        self.ids.compleat_Session_lable.text += f"You reviewed {self.total_today_reviews} cards today\n"
        self.ids.compleat_Session_lable.text += "Great job! Come back later for more reviews."
    
    def update_counter(self):
        """آپدیت شمارنده کارت‌ها"""
        counter_text = f"Card #{self.total_today_reviews}"
        self.ids.counter_label.text = counter_text
    
    def stop_playlist(self):
        """توقف پخش صداها"""
        try:
            self.ids.songs_playlist.on_stop()
        except:
            pass
    
    def refresh_session(self):
        """تازه‌سازی جلسه مرور"""
        self.show_answer = False
        self.session_completed = False
        self.stop_playlist()
        self.load_next_card()
    
    def show_success_indicator(self, message):
        """نمایش نشانگر موفقیت"""
        app = MDApp.get_running_app()
        if hasattr(app, 'show_message'):
            app.show_message(
                message=message,
                msg_type="success",
                duration=1
            )
    
    def show_error_message(self, message):
        """نمایش پیام خطا"""
        app = MDApp.get_running_app()
        if hasattr(app, 'show_message'):
            app.show_message(
                message=message,
                msg_type="error",
                duration=3
            )

    def fields_config(self):
        """تعریف کانفیگ فیلدها"""
        return [
            {
                'id': 'title_label',
                'attribute': 'text',
                'card_attribute': 'title',
                'default': '',
                'show_always': True
            },
            {
                'id': 'pronunciation_label',
                'attribute': 'text',
                'card_attribute': 'pronunciation',
                'default': '',
                'show_always': True
            },
            {
                'id': 'collocation_label',
                'attribute': 'text',
                'card_attribute': 'collocation',
                'default': '',
                'show_always': True
            },
            {
                'id': 'pos_chip',
                'attribute': 'text',
                'card_attribute': 'pos.caption',
                'default': '',
                'container': None,
                'show_always': False
            },
            {
                'id': 'type_chip',
                'attribute': 'text',
                'card_attribute': 'type_.caption',
                'default': '',
                'container': None,
                'show_always': False
            },
            {
                'id': 'level_chip',
                'attribute': 'text',
                'card_attribute': 'level.caption',
                'default': '',
                'container': None,
                'show_always': False
            },
            {
                'id': 'box_chip',
                'attribute': 'text',
                'card_attribute': 'box.caption',
                'default': '',
                'container': None,
                'show_always': False
            },
            {
                'id': 'past_tense_label',
                'attribute': 'text',
                'card_attribute': 'pastTense',
                'default': '',
                'container': 'verb_forms_box',
                'show_always': False
            },
            {
                'id': 'past_participle_label',
                'attribute': 'text',
                'card_attribute': 'pastParticiple',
                'default': '',
                'container': 'verb_forms_box',
                'show_always': False
            },
            {
                'id': 'example_label',
                'attribute': 'text',
                'card_attribute': 'example',
                'default': '',
                'container': 'example_box',
                'show_always': True
            },
            {
                'id': 'definition_label',
                'attribute': 'text',
                'card_attribute': 'definition',
                'default': '',
                'container': 'definition_box',
                'show_always': False
            },
            {
                'id': 'songs_playlist',
                'attribute': 'songs',
                'card_attribute': 'files',
                'default': [],
                'show_always': True
            }
        ]
    
    def _set_widget_value(self, widget_id, attribute, value):
        """تنظیم مقدار برای widget"""
        try:
            if widget_id in self.ids:
                widget = self.ids[widget_id]
                setattr(widget, attribute, value)

        except Exception as e:
            print(f"Error setting value for {widget_id}: {e}")