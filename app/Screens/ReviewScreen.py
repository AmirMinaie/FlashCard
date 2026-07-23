from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from cmn.resource_helper import *
from BL.FlashCardBL import FlashCardBL
from BL.DashboardBL import DashboardBL
from widgets.SnackbarManager import snackbar_manager , Msg_type
from kivy.properties import BooleanProperty, NumericProperty
from kivy.clock import Clock
from kivy.metrics import dp
from widgets.Playlist import Playlist
from cmn.logger import logger
from cmn.get_progress_color import get_progress_color

Builder.load_file(str(PathManager.app_path("Kv/ReviewScreen.kv")))

class FieldMode:
    init = 1
    show_answer = 2
    hide_answer = 3

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
        self.Review_Stats = DashboardBL().get_Review_Stats()
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
        self.Avg = self.Review_Stats.avg_words_reviewed_last_two_weeks
        if self.Avg == 0:
            self.Avg = 1
        self.ids.counter_label.color = get_progress_color(self.total_today_reviews / self.Avg)
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
            self.display_current_card()
                
        except Exception as e:
            logger.info(f"Error loading next card: {e}")
            snackbar_manager.show_snackbar( message="Error loading card. Please try again.", msg_type=Msg_type.error )

    def load_card_fields(self):
        card = self.current_card
        if not card:
            return

        self.ids.title_label.text = card.title or ""
        self.ids.pronunciation_label.text = card.pronunciation or ""
        self.ids.collocation_label.text = card.collocation or ""
        self.ids.example_label.text = card.example or ""

        playlist = self.ids.songs_playlist
        playlist.clear()

        for file in card.files or []:
            playlist.add_song({
                "id": file.id,
                "title" :file.title,
                "fileName": file.fileName,
                "value": file.filePath,
                "from_type_id": file.sourceType_id,
                "from_type_caption": file.sourceType.caption,
            })

    def show_answer_data(self):
        card = self.current_card
        if not card:
            return

        self.ids.pos_chip.text = card.pos.caption if card.pos else ""
        self.ids.type_chip.text = card.type_.caption if card.type_ else ""
        self.ids.level_chip.text = card.level.caption if card.level else ""
        self.ids.box_chip.text = card.box.caption if card.box else ""

        self.ids.past_tense_label.text = card.pastTense or ""
        self.ids.past_participle_label.text = card.pastParticiple or ""

        self.ids.definition_label.text = card.definition or ""

    def clear_answer_fields(self):
        for widget in (
            self.ids.pos_chip,
            self.ids.type_chip,
            self.ids.level_chip,
            self.ids.box_chip,
            self.ids.past_tense_label,
            self.ids.past_participle_label,
            self.ids.definition_label,
        ):
            widget.text = " "

    def set_fields(self, mode):
        if mode == FieldMode.init:
            self.load_card_fields()
            self.clear_answer_fields()

        elif mode == FieldMode.show_answer:
            self.show_answer_data()

        elif mode == FieldMode.hide_answer:
            self.clear_answer_fields()

    def show_card_content(self, show):
        """نمایش یا مخفی کردن محتوای کارت"""

        if show:
            self.set_widget_state(self.ids.flashcard_box, visible=True)
            self.ids.flashcard_box.size_hint_y = 0.9
            self.ids.flashcard_box.pos_hint = {"top": 0.9,"center_x": 0.5,}

            self.set_widget_state(self.ids.compleat_Session_Box,visible=False,height=0,)
            self.ids.compleat_Session_Box.size_hint_y = None

            self.set_widget_state(self.ids.button_box,visible=True,height=60,)

        else:
            self.set_widget_state(self.ids.flashcard_box, visible=False)
            self.ids.flashcard_box.size_hint_y = 0
    
    def hide_answer_fields(self):
        self.set_fields(mode=FieldMode.hide_answer)
        
        if not self.session_completed:
            self.ids.button_box.opacity = 1
            self.ids.button_box.disabled = False
        
        self.set_widget_state(self.ids.button_box,visible=True,height=dp(46))
        self.set_widget_state(self.ids.answer_button_box,visible=False,height=0)
    
        self.ids.button_area.height = dp(52)
        
        self.show_answer = False
     
    def show_session_completed(self):
        """نمایش پیام پایان جلسه مرور"""
        self.session_completed = True
        
        self.set_widget_state(self.ids.button_box, visible=False)
        self.set_widget_state(self.ids.answer_button_box, visible=False)
        self.set_widget_state(self.ids.flashcard_box, visible=False)
        self.set_widget_state(self.ids.compleat_Session_Box,visible=True,height=80)

        self.ids.compleat_Session_lable.text = "Session Completed!\n"
        self.ids.compleat_Session_lable.text += f"You reviewed {self.total_today_reviews} cards today\n"
        self.ids.compleat_Session_lable.text += "Great job! Come back later for more reviews."
    
    def stop_playlist(self):
        """توقف پخش صداها"""
        try:
            self.ids.songs_playlist.on_stop()
        except:
            pass
    
    def before_skip_card(self):
        self.stop_playlist()

    def skip_card(self):
        if self.current_card:
            self.flashcard_bl.mark_card_reviewed(
                card_id=self.current_card.id,
                quality_Answer=-1
            )

    def after_skip_card(self, result):
        snackbar_manager.show_snackbar( message=f"⏭ Skipped", msg_type=Msg_type.error )
        Clock.schedule_once(lambda dt: self.load_next_card(),0.5)

    def handle_skip_card_error(self, error):
        logger.error(f"Skip error: {error}")
        self.load_next_card()

    def show_answer_fields(self):

        if not self.current_card:
            return

        self.set_fields(mode=FieldMode.show_answer)

        self.set_widget_state(self.ids.button_box,visible=False,height=0)
        self.set_widget_state(self.ids.answer_button_box,visible=True,height=dp(46))

        self.ids.button_area.height = dp(52)

        self.show_answer = True

    def set_widget_state(self, widget, *, visible, height=None):
        widget.opacity = 1 if visible else 0
        widget.disabled = not visible

        if height is not None:
            widget.height = height

    def before_mark_quality(self):
        self.stop_playlist()
        return True

    def mark_card_quality0(self):
        self.mark_card_quality(0)

    def mark_card_quality1(self):
        self.mark_card_quality(1)

    def mark_card_quality2(self):
        self.mark_card_quality(2)

    def mark_card_quality3(self):
        self.mark_card_quality(3)

    def mark_card_quality4(self):
        self.mark_card_quality(4)

    def after_mark_quality0(self, result):
        self.after_mark_quality(0, result)

    def after_mark_quality1(self, result):
        self.after_mark_quality(1, result)

    def after_mark_quality2(self, result):
        self.after_mark_quality(2, result)

    def after_mark_quality3(self, result):
        self.after_mark_quality(3, result)

    def after_mark_quality4(self, result):
        self.after_mark_quality(4, result)

    def mark_card_quality(self, quality):

        if not self.current_card:
            return

        success = self.flashcard_bl.mark_card_reviewed(
            card_id=self.current_card.id,
            quality_Answer=quality
        )

        if success:
            self.total_today_reviews += 1
            self.ids.counter_label.color = get_progress_color(self.total_today_reviews / self.Avg)

    def after_mark_quality(self, quality , result):
        snackbar_manager.show_snackbar( message=f"✓ Saved {quality}", msg_type=Msg_type.success )
        Clock.schedule_once( lambda dt: self.load_next_card(), 0.5 )

    def handle_mark_quality_error(self, error):
        logger.error(f"Quality error: {error}")
        snackbar_manager.show_snackbar( message=f"Error saving review {str(error)}", msg_type=Msg_type.error )
    

    def before_refresh_session(self):
        self.stop_playlist()
        self.hide_answer_fields()
        return True

    def refresh_session(self):
        current_card = self.flashcard_bl.get_next_card_for_review()
        return current_card
        
    def after_refresh_session(self , result):
        self.current_card = result
        self.display_current_card()
        
    def handle_refresh_session_error(self,error):
        logger.error(f"Refresh error: {error}")
        snackbar_manager.show_snackbar( message="Cannot refresh session", msg_type=Msg_type.error )

    def display_current_card(self):
        if self.current_card:
            self.show_card_content(True)
            self.set_fields(mode=FieldMode.init)
        else:
            self.show_session_completed()
