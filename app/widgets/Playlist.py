import os

from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.properties import (
    StringProperty,
    NumericProperty,
    BooleanProperty,
    ListProperty,
)
from kivy.core.audio import SoundLoader

from cmn.resource_helper import resource_path


Builder.load_file(resource_path("app", "widgets", "Playlist.kv"))


class Playlist(MDBoxLayout):

    current_song = StringProperty("No song")

    volume_level = NumericProperty(50)

    is_playing = BooleanProperty(False)

    songs = ListProperty([])

    volume_slider_enabled = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.sound = None
        self.current_index = 0
        self.last_volume = 50

    # -------------------------
    # Load song
    # -------------------------

    def load_song(self, song):
        self.stop_player()

        try:
            path = resource_path("files", song.filePath)

            print("AUDIO PATH:", path)

            if not os.path.isfile(path):
                print("FILE NOT FOUND:", path)
                self.current_song = "File not found"
                return False

            sound = SoundLoader.load(path)

            print("AUDIO OBJECT:", sound)

            if sound is None:
                print("AUDIO LOAD FAILED:", path)
                self.current_song = "Unsupported audio"
                return False

            sound.volume = self.volume_level / 100
            sound.loop = False

            self.sound = sound
            self.current_song = song.fileName

            print("AUDIO LOADED SUCCESSFULLY")
            return True

        except Exception as e:
            print("LOAD ERROR:", repr(e))

            self.sound = None
            self.current_song = "Audio load error"
            self.is_playing = False

            return False

    # -------------------------
    # Play / Stop
    # -------------------------

    def toggle_play(self):
        if not self.sound:
            if not self.songs:
                print("PLAYLIST IS EMPTY")
                return

            if self.current_index >= len(self.songs):
                self.current_index = 0

            loaded = self.load_song(
                self.songs[self.current_index]
            )

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
            print("START PLAYING:", self.current_song)

            self.sound.play()

            self.is_playing = True

            print("PLAY STARTED")

        except Exception as e:
            print("PLAY ERROR:", repr(e))
            self.is_playing = False

    def stop_song(self):
        if not self.sound:
            return

        try:
            print("STOPPING:", self.current_song)

            self.sound.stop()

            self.is_playing = False

        except Exception as e:
            print("STOP ERROR:", repr(e))
            self.is_playing = False

    # -------------------------
    # Next / Previous
    # -------------------------

    def next_song(self):
        if not self.songs:
            print("PLAYLIST IS EMPTY")
            return

        was_playing = self.is_playing

        self.current_index = (
            self.current_index + 1
        ) % len(self.songs)

        loaded = self.load_song(
            self.songs[self.current_index]
        )

        if loaded and was_playing:
            self.play_song()

    def prev_song(self):
        if not self.songs:
            print("PLAYLIST IS EMPTY")
            return

        was_playing = self.is_playing

        self.current_index = (
            self.current_index - 1
        ) % len(self.songs)

        loaded = self.load_song(
            self.songs[self.current_index]
        )

        if loaded and was_playing:
            self.play_song()

    # -------------------------
    # Volume
    # -------------------------

    def set_volume(self, value):
        self.volume_level = value

        if value > 0:
            self.last_volume = value

        if self.sound:
            try:
                self.sound.volume = value / 100
            except Exception as e:
                print("VOLUME ERROR:", repr(e))

    def toggle_mute(self):
        if self.volume_level > 0:
            self.set_volume(0)
        else:
            if self.last_volume <= 0:
                self.last_volume = 50

            self.set_volume(self.last_volume)

    # -------------------------
    # Cleanup
    # -------------------------

    def stop_player(self):
        if self.sound:
            try:
                self.sound.stop()
            except Exception as e:
                print("STOP PLAYER ERROR:", repr(e))

        self.sound = None
        self.is_playing = False

    def on_stop(self):
        self.stop_player()