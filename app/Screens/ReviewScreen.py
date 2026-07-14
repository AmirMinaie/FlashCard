from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from cmn.resource_helper import *
from BL.FlashCardBL import FlashCardBL
from BL.DashboardBL import DashboardBL
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
from cmn.logger import logger
from cmn.logger import logger

Builder.load_file(str(PathManager.app_path("Kv/ReviewScreen.kv")))

class FieldMode:
    init = 1
    show_answer = 2
    hiden_answer = 3

class ReviewScreen(MDScreen):
    show_answer = BooleanProperty(False)
    current_card = None
    total_today_reviews = NumericProperty(0)
    remaining_cards = NumericProperty(0)
    session_completed = BooleanProperty(False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flashcard_bl = FlashCardBL()
        self.summary = DashboardBL().get_summary()
        self.current_card = None
        self.session_dialog = None
        self.no_more_cards_dialog = None
        self.parent_tab = None
    
    def on_parent(self, widget, parent):
        """وقتی صفحه به والد اضافه شد"""
        if parent:
            self.parent_tab = parent
    
    def on_kv_post(self, *args):
        """هر بار که وارد صفحه می‌شود"""
        self.show_answer = False
        self.session_completed = False
        self.total_today_reviews = self.summary.today_reviews
        self.load_next_card()
    
    def load_next_card(self):
        """لود کارت بعدی از دیتابیس"""
        try:
            # توقف پخش صداهای قبلی
            self.stop_playlist()
            
            # مخفی کردن بخش‌های جواب
            self.hide_answer_fields()
            
            self.current_card = self.flashcard_bl.get_next_card_for_review()
            self.remaining_cards = self.summary.remaining_reviews
            if self.current_card:
                self.show_card_content(True)
                self.set_fields(Mode=FieldMode.init)                
                self.update_counter()
                
            else:
                # اگر کارتی برای مرور نبود
                self.show_session_completed()
                
        except Exception as e:
            logger.info(f"Error loading next card: {e}")
            self.show_error_message("Error loading card. Please try again.")
    
    def set_fields(self, Mode):

        card = self.current_card

        if card:

            if Mode == FieldMode.init:

                self.ids.title_label.text = card.title or ""
                self.ids.pronunciation_label.text = card.pronunciation or ""
                self.ids.collocation_label.text = card.collocation or ""
                self.ids.example_label.text = card.example or ""
                self.ids.songs_playlist.clear()
                if card.files:
                    for file in card.files:
                        item = {
                            "id": file.id,
                            "fileName": file.fileName,
                            "value": file.filePath,
                            "from_type_id": file.sourceType_id,
                            "from_type_caption": file.sourceType.caption
                        }
                        self.ids.songs_playlist.add_song(item)

            if Mode == FieldMode.show_answer:
                self.ids.pos_chip.text = card.pos.caption if card.pos else ""
                self.ids.type_chip.text = card.type_.caption if card.type_ else ""
                self.ids.level_chip.text = card.level.caption if card.level else ""
                self.ids.box_chip.text = card.box.caption if card.box else ""

                self.ids.past_tense_label.text = card.pastTense or ""
                self.ids.past_participle_label.text = card.pastParticiple or ""

                self.ids.definition_label.text = card.definition or ""

            if Mode == FieldMode.hiden_answer or Mode == FieldMode.init: 
                self.ids.pos_chip.text = "  "
                self.ids.type_chip.text = " "
                self.ids.level_chip.text = " "
                self.ids.box_chip.text = " "

                self.ids.past_tense_label.text = " "
                self.ids.past_participle_label.text = " "

                self.ids.definition_label.text = " "

    def show_card_content(self, show):
        """نمایش یا مخفی کردن محتوای کارت"""
        if show:
            self.ids.flashcard_box.opacity = 1
            self.ids.flashcard_box.disabled = False
            self.ids.flashcard_box.size_hint_y = 0.9
            self.ids.flashcard_box.pos_hint = {"top": 0.9, "center_x": 0.5}
            
            self.ids.compleat_Session_Box.opacity = 0
            self.ids.compleat_Session_Box.disabled = True
            self.ids.compleat_Session_Box.size_hint_y = None
            self.ids.compleat_Session_Box.height = 0
            
            # فعال کردن دکمه‌ها
            self.ids.button_box.opacity = 1
            self.ids.button_box.disabled = False
            self.ids.button_box.height = 60
        else:
            self.ids.flashcard_box.opacity = 0
            self.ids.flashcard_box.disabled = True
            self.ids.flashcard_box.size_hint_y = 0

    def show_answer_fields(self):
        """نمایش فیلدهای جواب"""
        if not self.current_card:
            return
            
        self.set_fields(Mode=FieldMode.show_answer)
        
        # تغییر دکمه‌ها
        self.ids.button_box.height = 0
        self.ids.button_box.opacity = 0
        self.ids.button_box.disabled = True

        self.ids.answer_button_box.height = dp(46)
        self.ids.answer_button_box.opacity = 1
        self.ids.answer_button_box.disabled = False

        self.ids.button_area.height = dp(52)
        
        self.show_answer = True
    
    def hide_answer_fields(self):
        # ریست کردن مقادیر
        self.set_fields(Mode=FieldMode.hiden_answer)
        
        # تغییر وضعیت دکمه‌ها
        if not self.session_completed:
            self.ids.button_box.opacity = 1
            self.ids.button_box.disabled = False
        
        # تغییر دکمه‌ها
        self.ids.button_box.height = dp(46)
        self.ids.button_box.opacity = 1
        self.ids.button_box.disabled = False
    
        self.ids.answer_button_box.height = 0
        self.ids.answer_button_box.opacity = 0
        self.ids.answer_button_box.disabled = True
    
        self.ids.button_area.height = dp(52)
        
        self.show_answer = False
     
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
            logger.info(f"Error marking card correct: {e}")
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
            logger.info(f"Error skipping card: {e}")
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
        self.ids.compleat_Session_Box.height = 80

        
        # نمایش پیام در کارت
        
        self.ids.compleat_Session_lable.text = "Session Completed!\n"
        self.ids.compleat_Session_lable.text += f"You reviewed {self.total_today_reviews} cards today\n"
        self.ids.compleat_Session_lable.text += "Great job! Come back later for more reviews."
    
    def update_counter(self):
        """آپدیت شمارنده کارت‌ها"""
        counter_text = f"Done: {self.total_today_reviews} | Remaining: {self.remaining_cards}"
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
            