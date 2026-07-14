import os
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.properties import ( StringProperty, NumericProperty, BooleanProperty, ListProperty, ObjectProperty)
from BL.fileManager import FileManager
from kivy.core.audio import SoundLoader
from kivymd.uix.slider import MDSlider
from cmn.resource_helper import *
from kivy.metrics import dp
from kivy.clock import Clock
from widgets.BaseButtonA import BaseButtonA
from kivymd.uix.list import OneLineRightIconListItem, IconRightWidget
import uuid

Builder.load_string(
    
"""
<Playlist>:
    orientation: "vertical"
    padding: dp(15)
    spacing: dp(8)

    MDBoxLayout:
        size_hint_y: None
        height: dp(75)
        spacing: dp(8)

        MDBoxLayout:
            size_hint_x: 0.35
            padding: dp(5)

            MDLabelA:
                text: root.current_song
                shorten: True
                shorten_from: "right"
                max_lines: 1
                halign: "left"
                valign: "middle"
                text_size: self.size

        MDBoxLayout:
            size_hint_x: 0.35
            spacing: dp(8)
            padding: dp(0), dp(8)
            pos_hint: {"center_x": 0.5}

            MDIconButton:
                icon: "skip-previous"
                icon_size: dp(30)
                on_release: root.prev_song()

            MDFloatingActionButton:
                icon: "pause" if root.is_playing else "play"
                size_hint: None, None
                size: dp(52), dp(52)
                on_release: root.toggle_play()

            MDIconButton:
                icon: "skip-next"
                icon_size: dp(30)
                on_release: root.next_song()

        MDBoxLayout:
            size_hint_x: 0.30
            spacing: dp(4)
            padding: dp(0), dp(10)
            opacity: 1 if root.volume_slider_enabled else 0
            disabled: not root.volume_slider_enabled

            MDIconButton:
                icon: "volume-high" if root.volume_level > 0 else "volume-off"
                on_release: root.toggle_mute()

            MDSlider:
                min: 0
                max: 100
                value: root.volume_level
                on_value: root.set_volume(self.value)
    
    ScrollView:
        size_hint_y: 1
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            height: self.minimum_height

            MDLabelA:
                text: "Playlist is empty"
                halign: "center"
                valign: "middle"
                size_hint_y: None
                height: dp(50) if len(root.songs) == 0 else 0
                opacity: 1 if len(root.songs) == 0 else 0
                disabled: len(root.songs) != 0

            MDList:
                id: song_list
                size_hint_y: None
                height: self.minimum_height
""")


class Playlist(MDBoxLayout):

    current_song = StringProperty("No song")
    volume_level = NumericProperty(100)
    allow_delete = BooleanProperty(False)
    is_playing = BooleanProperty(False)
    songs = ListProperty([])
    volume_slider_enabled = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.song_widgets = {}
        self.sound = None
        self.current_index = 0
        self.last_volume = 100

    def show_message(self, message, msg_type="info"):
        app = MDApp.get_running_app()
        app.show_message(   message,   msg_type=msg_type, duration=5   )

    def load_song(self, song):
        self.stop_player()

        try:
            path = FileManager.getfilepath(song["value"])

            if not os.path.isfile(path):
                self.show_message("File not found", "error")
                self.current_song = "File not found"
                return False

            sound = SoundLoader.load(path)

            if sound is None:
                self.show_message("Audio file is not supported or corrupted", "error")
                self.current_song = "Unsupported audio"
                return False

            sound.volume = self.volume_level / 100
            sound.loop = False

            self.sound = sound
            self.current_song = song["fileName"]

            return True

        except Exception as e:
            self.show_message(f"Unexpected error while loading audio {str(e)}", "error")
            self.sound = None
            self.current_song = "Audio error"
            self.is_playing = False
            return False

    def toggle_play(self):
        if not self.sound:
            if not self.songs:
                self.show_message("Playlist is empty", "warning")
                return

            if self.current_index >= len(self.songs):
                self.current_index = 0

            loaded = self.load_song(self.songs[self.current_index])

            if not loaded:
                return

        if self.is_playing:
            self.stop_song()
        else:
            self.play_song()

    def play_song(self):
        if not self.sound:
            return

        try:
            self.sound.play()
            self.is_playing = True

        except Exception:
            self.show_message("Cannot play this audio file", "error")
            self.is_playing = False

    def stop_song(self):
        if not self.sound:
            return

        try:
            self.sound.stop()
            self.is_playing = False

        except Exception:
            self.show_message("Error while stopping audio", "error")
            self.is_playing = False

    def next_song(self):
        if not self.songs:
            self.show_message("Playlist is empty", "warning")
            return

        was_playing = self.is_playing
        self.current_index = (self.current_index + 1) % len(self.songs)
        loaded = self.load_song(self.songs[self.current_index])

        if loaded and was_playing:
            self.play_song()

    def prev_song(self):
        if not self.songs:
            self.show_message("Playlist is empty", "warning")
            return

        was_playing = self.is_playing
        self.current_index = (self.current_index - 1) % len(self.songs)
        loaded = self.load_song(self.songs[self.current_index])
        if loaded and was_playing:
            self.play_song()

    def set_volume(self, value):
        self.volume_level = value

        if value > 0:
            self.last_volume = value

        if self.sound:
            try:
                self.sound.volume = value / 100
            except Exception:
                self.show_message("Volume error", "error")

    def toggle_mute(self):
        if self.volume_level > 0:
            self.set_volume(0)
        else:
            if self.last_volume <= 0:
                self.last_volume = 50

            self.set_volume(self.last_volume)

    def stop_player(self):
        if self.sound:
            try:
                self.sound.stop()
            except Exception:
                self.show_message("Audio stop error", "error")

        self.sound = None
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

        text = song["fileName"]
    
        item = OneLineRightIconListItem(text=text)
        item.song = song
    
        item.bind(on_release=lambda x: self.select_song(x.song))
    
        if self.allow_delete:
            btn = IconRightWidget(icon="delete")
            btn.song = song
            btn.bind(on_release=lambda x: self.delete_song(x.song))
            item.add_widget(btn)
    
        return item

    def clear(self):
        self.stop_player()
        self.songs = []
        self.current_song = "No song"
        self.current_index = 0
        self.ids.song_list.clear_widgets()