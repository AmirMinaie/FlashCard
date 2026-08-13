import os
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from app.widgets.SnackbarManager import snackbar_manager , Msg_type
from kivy.properties import ( StringProperty, NumericProperty, BooleanProperty, ListProperty, ObjectProperty)
from app.BL.fileManager import FileManager
from app.widgets.AudioPlayer import AudioPlayer , PlayerState
from kivymd.uix.slider import MDSlider
from app.cmn.resource_helper import *
from kivy.metrics import dp
from kivy.clock import Clock
from app.widgets.BaseButtonA import BaseButtonA
from kivymd.uix.list import OneLineRightIconListItem, IconRightWidget
from app.widgets.SongItem import SongItem
import uuid
import threading
from app.BL.FlashCardBL import FlashCardBL
from app.cmn.logger import logger
from app.cmn.utility import *


Builder.load_string(
    
"""
<Playlist>:
    orientation: "vertical"
    padding: dp(12)
    spacing: dp(4)

    # =========================================================
    # PROGRESS
    # =========================================================

    MDBoxLayout:
        size_hint_y: None
        height: dp(32)
        padding: dp(4), 0

        MDSlider:
            id: progress_slider

            min: 0
            max: max(root.current_duration, 0.1)
            value: root.current_position

            size_hint_y: None
            height: dp(32)

            on_touch_down: root.start_seek() if self.collide_point(*args[1].pos) else None
            on_touch_up: root.finish_seek(self.value) if self.collide_point(*args[1].pos) else None
    # =========================================================
    # PLAYER CONTROLS
    # =========================================================

    MDBoxLayout:
        size_hint_y: None
        height: dp(68)
        spacing: dp(6)

        # -----------------------------------------------------
        # CURRENT SONG
        # -----------------------------------------------------

        MDBoxLayout:
            size_hint_x: 0.36
            orientation: "vertical"
            padding: dp(4), dp(7)
            spacing: dp(2)

            MDLabelA:
                text: root.current_song
                shorten: True
                shorten_from: "right"
                max_lines: 1
                halign: "left"
                valign: "bottom"
                text_size: self.size

            MDLabelA:
                id: time_label
                text: f"{root.current_time_text} / {root.duration_text}"
                size_hint_y: None
                height: dp(20)
                font_size: "12sp"
                theme_text_color: "Secondary"
                halign: "left"
                valign: "top"
                text_size: self.size

        # -----------------------------------------------------
        # MAIN CONTROLS
        # -----------------------------------------------------

        MDBoxLayout:
            size_hint_x: 0.28
            spacing: dp(2)
            padding: 0
            pos_hint: {"center_y": 0.5}

            MDIconButton:
                icon: "skip-previous"
                icon_size: dp(27)
                pos_hint: {"center_y": 0.5}
                on_release: root.prev_song()

            MDFloatingActionButton:
                icon: "pause" if root.is_playing else "play"
                size_hint: None, None
                size: dp(48), dp(48)
                pos_hint: {"center_y": 0.5}
                elevation: 2
                on_release: root.toggle_play()

            MDIconButton:
                icon: "skip-next"
                icon_size: dp(27)
                pos_hint: {"center_y": 0.5}
                on_release: root.next_song()

        # -----------------------------------------------------
        # VOLUME
        # -----------------------------------------------------

        MDBoxLayout:
            size_hint_x: 0.36
            spacing: dp(3)
            padding: dp(2), dp(8)
            pos_hint: {"center_y": 0.5}

            opacity: 1 if root.volume_slider_enabled else 0
            disabled: not root.volume_slider_enabled

            MDIconButton:
                icon: "volume-high" if root.volume_level > 0 else "volume-off"
                icon_size: dp(23)
                pos_hint: {"center_y": 0.5}
                on_release: root.toggle_mute()

            MDSlider:
                min: 0
                max: 100
                value: root.volume_level
                size_hint_y: None
                height: dp(32)
                pos_hint: {"center_y": 0.5}
                on_value: root.set_volume(self.value)

    # =========================================================
    # PLAYLIST
    # =========================================================

    ScrollView:
        size_hint_y: 1
        do_scroll_x: False
        bar_width: dp(3)

        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            height: self.minimum_height
            spacing: dp(4)

            MDLabelA:
                text: "Playlist is empty"
                halign: "center"
                valign: "middle"
                size_hint_y: None
                height: dp(50) if not root.songs else 0
                opacity: 1 if not root.songs else 0
                disabled: bool(root.songs)

            MDList:
                id: song_list
                size_hint_y: None
                spacing: dp(6)
                padding: dp(4), dp(4)
                height: self.minimum_height
""")


class Playlist(MDBoxLayout):

    current_position = NumericProperty(0.0)
    current_duration = NumericProperty(0.0)

    current_time_text = StringProperty("00:00")
    duration_text = StringProperty("00:00")

    current_song = StringProperty("No song")
    volume_level = NumericProperty(100)
    allow_delete = BooleanProperty(False)
    is_playing = BooleanProperty(False)
    songs = ListProperty([])
    volume_slider_enabled = BooleanProperty(True)

    is_seeking = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.audio_player = AudioPlayer()
        self.audio_player.on_finished = self._on_song_finished
        self.audio_player.on_error = self._on_player_error

        self.song_widgets = {}
        self.current_index = 0
        self.last_volume = 100

        self.current_song_id = None

        self._position_event = Clock.schedule_interval(
            self._update_position,
            0.2
        )

    def _update_position(self, dt):
        if not self.audio_player:
            return

        if not self.is_seeking:
            self.current_position = self.audio_player.position
        self.current_duration = self.audio_player.duration

        self.current_time_text = format_time( self.current_position )
        self.duration_text = format_time( self.current_duration )   

        self.is_playing = self.audio_player.is_playing()

    def load_song(self, song):
        try:
            path = FileManager.getfilepath(song["value"])

            if not os.path.isfile(path):
                snackbar_manager.show_snackbar(
                    message="File not found",
                    msg_type=Msg_type.error
                )
                self.current_song = "File not found"
                return False

            loaded = self.audio_player.load(path)

            if not loaded:
                snackbar_manager.show_snackbar(
                    message="Audio file could not be loaded",
                    msg_type=Msg_type.error
                )
                self.current_song = "Unsupported audio"
                return False

            self.audio_player.set_volume(self.volume_level)

            # آهنگی که واقعاً load شده
            self.current_song_id = song.get("id")

            self.current_song = song["fileName"]

            return True

        except Exception as e:
            logger.error(
                f"Unexpected error while loading audio: {str(e)}"
            )

            snackbar_manager.show_snackbar(
                message=f"Unexpected error while loading audio: {e}",
                msg_type=Msg_type.error
            )

            self.current_song = "Audio error"
            self.is_playing = False

            return False
    
    def toggle_play(self):
        if not self.songs:
            snackbar_manager.show_snackbar(
                message="Playlist is empty",
                msg_type=Msg_type.warning
            )
            return

        if self.audio_player.is_playing():
            self.audio_player.pause()
            self.is_playing = False
            return

        if self.audio_player.is_paused():
            self.audio_player.resume()
            self.is_playing = True
            return

        if self.audio_player.is_finished():
            self.audio_player.seek(0)
            self.audio_player.play()
            self.is_playing = True
            return

        if self.audio_player.is_loaded():
            self.audio_player.play()
            self.is_playing = True
            return

        if self.current_index >= len(self.songs):
            self.current_index = 0

        loaded = self.load_song(
            self.songs[self.current_index]
        )

        if loaded:
            self.play_song()

    def play_song(self):
        if self.audio_player is None:
            return

        try:
            if self.audio_player.play():
                self.is_playing = True

        except Exception as e:
            logger.eror("Cannot play audio")

            snackbar_manager.show_snackbar(
                message="Cannot play this audio file",
                msg_type=Msg_type.error
            )

            self.is_playing = False

    def _increment_view_count(self, file_id):
        try:
            flashCard_BL = FlashCardBL()
            count = flashCard_BL.view_file(file_id)
            logger.debug(f"increment_view_count {count}")
        except Exception as e:
            logger.error(f"Error incrementing view count: {e}")

    def stop_song(self):
        if self.audio_player is None:
            return

        try:
            self.audio_player.pause()
            self.is_playing = False

        except Exception:
            snackbar_manager.show_snackbar(
                message="Error while stopping audio",
                msg_type=Msg_type.error
            )
            self.is_playing = False

    def next_song(self, auto_play=True):
        if not self.songs:
            snackbar_manager.show_snackbar(
                message="Playlist is empty",
                msg_type=Msg_type.warning
            )
            return

        self.current_index = (
            self.current_index + 1
        ) % len(self.songs)

        loaded = self.load_song(
            self.songs[self.current_index]
        )

        if loaded and auto_play:
            self.play_song()

    def prev_song(self):
        if not self.songs:
            snackbar_manager.show_snackbar(
                message="Playlist is empty",
                msg_type=Msg_type.warning
            )
            return

        self.current_index = (
            self.current_index - 1
        ) % len(self.songs)

        loaded = self.load_song(
            self.songs[self.current_index]
        )

        if loaded:
            self.play_song()

    def set_volume(self, value):
        self.volume_level = value

        if value > 0:
            self.last_volume = value

        if self.audio_player:
            self.audio_player.set_volume(value)

    def toggle_mute(self):
        if self.volume_level > 0:
            self.last_volume = self.volume_level
            self.set_volume(0)
        else:
            if self.last_volume <= 0:
                self.last_volume = 50

            self.set_volume(self.last_volume)

    def stop_player(self):
        if self.audio_player:
            self.audio_player.release()

        self.is_playing = False

    def on_stop(self):
        self.stop_player()
    
    def delete_song(self, song):
        try:
            self.songs.remove(song)

            song_id = song["id"]
            widget = self.song_widgets.pop(song_id, None)
            if widget:
                self.ids.song_list.remove_widget(widget)

        except ValueError:
            pass

    def select_song(self, song):
        loaded = self.load_song(song)

        if loaded:
            self.play_song()
    
    def add_song(self, song):
        if 'id' not in song:
            song['id'] = f"new_{uuid.uuid4()}"

        self.songs.append(song)
        widget = self.create_song_widget(song)
        self.song_widgets[song["id"]] = widget
        self.ids.song_list.add_widget(widget)
        self.ids.song_list.height = self.ids.song_list.minimum_height

    def create_song_widget(self, song):

        fileName = song["fileName"]
        title = song.get("title", "")
        
        if title and title.strip():
            text = title
        else:
            text = fileName
    
        text = f'{song.get("view_count", "0")} - {text}'
        item = SongItem( text=text, song=song, allow_delete=self.allow_delete, )

        item.song = song
        
        item.select_callback = self.select_song
        
        if self.allow_delete:
            item.delete_callback = self.delete_song
    
        return item

    def clear(self):
        if self.audio_player:
            self.audio_player.release()

        self.songs = []
        self.current_song = "No song"
        self.current_index = 0
        self.is_playing = False

        self.song_widgets.clear()
        self.ids.song_list.clear_widgets()

    def _on_song_finished(self):
        self.is_playing = False

        file_id = self.current_song_id

        if file_id is None:
            return

        threading.Thread(
            target=self._increment_view_count,
            args=(file_id,),
            daemon=True
        ).start()

    def _on_player_error(self, error):
        self.is_playing = False

        snackbar_manager.show_snackbar(
            message="Audio playback error",
            msg_type=Msg_type.error
        )

        logger.error(f"AudioPlayer error: {error}")

    def finish_seek(self, value):
        self.is_seeking = False

        if self.audio_player:
            self.audio_player.seek(float(value))

    def start_seek(self):
        self.is_seeking = True