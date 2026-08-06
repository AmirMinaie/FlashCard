from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from functools import partial
import time
from cmn.resource_helper import *
from BL.FlashCardBL import FlashCardBL
from BL.DashboardBL import DashboardBL
from widgets.SnackbarManager import snackbar_manager , Msg_type
from kivy.properties import BooleanProperty, NumericProperty , StringProperty
from kivy.clock import Clock
from kivy.metrics import dp
from widgets.Playlist import Playlist
from cmn.logger import logger
from cmn.utility import  *
from enum import Enum, auto

Builder.load_file(str(PathManager.app_path("Kv/ReviewScreen.kv")))

class SessionState(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()

class FieldMode:
    init = 1
    show_answer = 2
    hide_answer = 3

class ReviewScreen(MDScreen):
    show_answer = BooleanProperty(False)
    current_card = None
    total_today_reviews = NumericProperty(0)
    remaining_cards = NumericProperty(0)
    session_time = StringProperty("0s")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flashcard_bl = FlashCardBL()
        self.dashboard_bl = DashboardBL()
        self.summary = self.dashboard_bl.get_summary()
        self.Review_Stats = self.dashboard_bl.get_Review_Stats()
        self.current_card = None
        self.session_dialog = None
        self.no_more_cards_dialog = None
        self.parent_tab = None
        self.card_start_time = None
        self.answer_show_time = None
        self.thinking_time = 0
        self.session_state = None
        self.arrow = ""
        self.session_start_time = None
        self.session_timer = None
        self.elapsed_time = 0
        self.pause_start_time = None

    def set_session_state(self, state: SessionState):
        old_state = self.session_state
        if old_state == state:
            return

        self.session_state = state
        self.update_toggle_button()

        match state:

            case SessionState.RUNNING:
                self.start_session_timer()

                if old_state == SessionState.PAUSED and self.current_card:
                    self.update_layout(True)

                    if self.show_answer:
                        self.set_widget_state(self.ids.button_box,visible=False,height=0)
                        self.set_widget_state(self.ids.answer_button_box,visible=True,height=dp(46))

                    else:
                        self.set_widget_state(self.ids.button_box,visible=True,height=dp(46))
                        self.set_widget_state(self.ids.answer_button_box,visible=False,height=0)

                    return

                self.move_to_next_card()

            case SessionState.PAUSED:
                self.stop_session_timer()
                self.stop_playlist()
                self.show_session_status(SessionState.PAUSED)
                self.update_layout(False)

            case SessionState.COMPLETED:
                self.stop_session_timer()
                self.stop_playlist()

                self.current_card = None
                self.show_answer = False

                self.show_session_status(SessionState.COMPLETED)

            case SessionState.STOPPED:
                self.stop_session_timer()
                self.stop_playlist()

                self.current_card = None
                self.show_answer = False
                self.show_session_status(SessionState.STOPPED)
                self.update_layout(False)

        self.update_toggle_button()

    def toggle_session(self):

        next_state = {
            SessionState.STOPPED: SessionState.RUNNING,
            SessionState.RUNNING: SessionState.PAUSED,
            SessionState.PAUSED: SessionState.RUNNING,
            SessionState.COMPLETED: SessionState.RUNNING,
        }

        next_session_state = next_state.get(self.session_state)
    
        if next_session_state is not None:
            self.set_session_state(next_session_state)

    def update_session_time(self , dt):
        current_elapsed = int(time.perf_counter() - self.session_start_time)
        total_elapsed = self.elapsed_time + current_elapsed

        self.session_time = format_time(total_elapsed)

    def start_session_timer(self):

        if self.session_timer:
            self.session_timer.cancel()

        self.session_start_time = time.perf_counter()
        self.session_timer = Clock.schedule_interval(self.update_session_time, 1)

    def stop_session_timer(self):
        if self.session_timer:
            self.session_timer.cancel()
            self.session_timer = None

            if self.session_start_time is not None:
                current_elapsed = int(time.perf_counter() - self.session_start_time)
                self.elapsed_time += current_elapsed
                self.session_start_time = None

    def reset_session_timer(self):
        """ریست کامل تایمر (برای session جدید)"""
        if self.session_timer:
            self.session_timer.cancel()
            self.session_timer = None

        self.session_start_time = None
        self.elapsed_time = 0
        self.session_time = "0s"

    def on_parent(self, widget, parent):
        """وقتی صفحه به والد اضافه شد"""
        if parent:
            self.parent_tab = parent
    
    def on_kv_post(self, *args):
        """هر بار که وارد صفحه می‌شود"""
        self.show_answer = False
        self.total_today_reviews = self.summary.today_reviews
        self.Avg = self.Review_Stats.avg_words_reviewed_last_two_weeks
        if self.Avg == 0:
            self.Avg = 1

        self.arrow = f"{arrow(0)}"
        self.set_widget_state( self.ids.counter_label, color=get_progress_color(self.total_today_reviews / self.Avg), )
        self.reset_session_timer()
        self.set_session_state(SessionState.STOPPED)
  
    def load_next_card(self):
        try:
            self.stop_playlist()

            card = self.flashcard_bl.get_next_card_for_review()

            self.summary = self.dashboard_bl.get_summary()
            self.remaining_cards = self.summary.remaining_reviews

            return card

        except Exception as error:
            logger.exception(f"Error loading next card: {error}")

            snackbar_manager.show_snackbar(
                message="Error loading card. Please try again.",
                msg_type=Msg_type.error
            )

            return None

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

    def update_layout(self, show_card: bool):
        """تنها متد مسئول نمایش Layout صفحه"""
    
        self.set_widget_state(
            self.ids.flashcard_box,
            visible=show_card,
            size_hint_y=1 if show_card else None,
            height=0,
        )
    
        self.set_widget_state(
            self.ids.compleat_Session_Box,
            visible=not show_card,
            size_hint_y=None if show_card else 1,
            height=0,
        )
    
        self.set_widget_state(
            self.ids.button_area,
            visible=show_card,
            height= dp(52) if show_card else 0,
        )

    def hide_answer_fields(self):
        self.set_fields(FieldMode.hide_answer)
        self.set_widget_state(self.ids.button_box,visible=True,height=dp(46),)
        self.set_widget_state( self.ids.answer_button_box, visible=False, height=0, )
        self.set_widget_state( self.ids.button_area, height=dp(52), )

        self.show_answer = False
     
    def show_session_status(self, state):

        if state == SessionState.STOPPED:
            icon = "play-circle-outline"
            title = "Ready to Review"
            description = "Press Start to begin your review session."

        elif state == SessionState.PAUSED:
            icon = "pause-circle-outline"
            title = "Session Paused"
            description = "Press Start to continue reviewing."

        elif state == SessionState.COMPLETED:
            icon = "check-decagram"
            title = "Session Completed"
            description = f"You reviewed {self.total_today_reviews} cards today."

        else:
            return

        self.set_widget_state(self.ids.session_status_icon, icon=icon)
        self.set_widget_state(self.ids.session_title, text=title)
        self.set_widget_state(self.ids.session_description, text=description)

    def stop_playlist(self):
        """توقف پخش صداها"""
        try:
            self.ids.songs_playlist.on_stop()
        except:
            pass
    
    def before_skip_card(self):
        self.stop_playlist()
        return True

    def skip_card(self):
        if not self.current_card:
            return False

        success= self.flashcard_bl.mark_card_reviewed(
            card_id=self.current_card.id,
            quality_Answer=-1,
            thinking_time=-1,
            answer_time=-1,
            total_time=-1
        )

        return {
                    "success": success,
                    "answer_time": -1,
                    "total_time": -1,
                }

    def after_skip_card(self, result):
        if not result:
            snackbar_manager.show_snackbar( message="Could not skip card.", msg_type=Msg_type.error )
            return

        snackbar_manager.show_snackbar( message="⏭ Skipped", msg_type=Msg_type.success )
        Clock.schedule_once( self.move_to_next_card, 0.01 )

    def handle_skip_card_error(self, error):
        logger.error(f"Skip error: {error}")

        self.set_session_state(SessionState.RUNNING)

    def show_answer_fields(self):

        if not self.current_card:
            return

        self.set_fields(mode=FieldMode.show_answer)

        self.set_widget_state(self.ids.button_box,visible=False,height=0)
        self.set_widget_state(self.ids.answer_button_box,visible=True,height=dp(46))
        self.set_widget_state( self.ids.button_area, height=dp(52))

        self.show_answer = True
        self.thinking_time = (time.perf_counter() - self.card_start_time)
        self.answer_show_time = time.perf_counter()

    def set_widget_state(self, widget, **kwargs):
        visible = kwargs.pop("visible", None)

        if visible is not None:
            widget.opacity = 1 if visible else 0
            widget.disabled = not visible

        for prop, value in kwargs.items():
            setattr(widget, prop, value)

    def before_mark_quality(self):
        self.stop_playlist()
        return True

    def quality_task(self, quality):
        return partial(self.mark_card_quality, quality)

    def quality_after(self, result):
        return partial(self.after_mark_quality, result)
    
    def mark_card_quality(self, quality):
        if not self.current_card:
            return False

        if self.answer_show_time is None:
            raise RuntimeError("Answer must be shown before rating the card.")

        answer_time = time.perf_counter() - self.answer_show_time
        total_time = self.thinking_time + answer_time

        success = self.flashcard_bl.mark_card_reviewed(
            card_id=self.current_card.id,
            quality_Answer=quality,
            thinking_time=self.thinking_time,
            answer_time=answer_time,
            total_time=total_time
        )

        return {
            "success": success,
            "answer_time": answer_time,
            "total_time": total_time,
        }

    def after_mark_quality(self, quality, result):
        if not result or not result.get("success"):
            snackbar_manager.show_snackbar( message="Review was not saved.", msg_type=Msg_type.error )
            return

        self.answer_time = result["answer_time"]
        self.total_time = result["total_time"]

        self.total_today_reviews += 1

        progress = self.total_today_reviews / self.Avg
        self.arrow = f"{arrow(progress)}"
        self.ids.counter_label.color = get_progress_color(progress)

        snackbar_manager.show_snackbar(
            message=(f"✓ Saved {quality}\n"f"Thinking {format_time(self.thinking_time)}\n"f"Answer {format_time(self.answer_time)}"),
            msg_type=Msg_type.success
        )

        Clock.schedule_once(self.move_to_next_card,0.01)

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
        
    def after_refresh_session(self, result):
        if not result:
            self.current_card = None
            self.set_session_state(SessionState.COMPLETED)
            return

        self.current_card = result

        self.summary = self.dashboard_bl.get_summary()
        self.remaining_cards = self.summary.remaining_reviews

        self.display_current_card()
        
    def handle_refresh_session_error(self,error):
        logger.error(f"Refresh error: {error}")
        snackbar_manager.show_snackbar( message="Cannot refresh session", msg_type=Msg_type.error )

    def display_current_card(self):
        if not self.current_card:
            return
        self.update_layout(True)
        self.set_fields(mode=FieldMode.init)
        self.card_start_time = time.perf_counter()
        self.answer_show_time = None

    def before_reload_card(self):
        self.stop_playlist()
        self.hide_answer_fields()
        return True

    def reload_current_card(self):
        if not self.current_card:
            return None
        return self.flashcard_bl.get_card_by_id(self.current_card.id)

    def after_reload_card(self, result):
        if result:
            self.current_card = result
            self.display_current_card()
        else:
            snackbar_manager.show_snackbar(message="Card not found in database.", msg_type=Msg_type.error)

    def handle_reload_card_error(self, error):
        logger.error(f"Reload card error: {error}")
        snackbar_manager.show_snackbar(
            message="Failed to reload card data.", msg_type=Msg_type.error
        )

    def move_to_next_card(self, dt=0):
        if self.session_state != SessionState.RUNNING:
            return

        self.current_card = None

        card = self.load_next_card()

        self.set_widget_state(self.ids.button_box,visible=True,height=dp(46))
        self.set_widget_state(self.ids.answer_button_box,visible=False,height=0)

        if card:
            self.current_card = card
            self.display_current_card()
        else:
            self.set_session_state(SessionState.COMPLETED)

    def update_toggle_button(self):
        self.set_widget_state(
            self.ids.toggle_session_btn,
            icon="pause" if self.session_state == SessionState.RUNNING else "play",
            disabled=False,
        )