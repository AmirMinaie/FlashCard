# audio_player.py
from enum import Enum
from cmn.logger import logger
import os

import pygame
from kivy.clock import Clock

class PlayerState(Enum):
    EMPTY = "empty"
    LOADED = "loaded"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    FINISHED = "finished"
    ERROR = "error"


class AudioPlayer:
    END_EVENT = pygame.USEREVENT + 1

    def __init__(self):
        self.metadata = None

        self._path = None
        self.state = PlayerState.EMPTY

        self.volume = 100
        self.loop = False
        self.muted = False

        self.error_message = None

        self.duration = 0.0
        self.position = 0.0

        self.on_finished = None
        self.on_error = None
        self.on_state_changed = None

        self._monitor_event = None
        self._pygame_initialized = False
        self._end_event_registered = False

        self._last_position = 0.0

        self._init_mixer()
        pygame.mixer.music.set_endevent(self.END_EVENT)

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def _init_mixer(self):
        """Initialize pygame mixer."""

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=2,
                    buffer=512,
                )

            self._pygame_initialized = True
            pygame.mixer.music.set_endevent(self.END_EVENT)
            self._end_event_registered = True

            logger.info("Pygame mixer initialized")

        except Exception as e:
            logger.error("Failed to initialize pygame mixer")
            self._notify_error(e)
            self._change_state(PlayerState.ERROR)

    # =========================================================
    # LOAD
    # =========================================================

    def load(self, path):
        """Load a new audio file."""

        if not self._pygame_initialized:
            self._notify_error("Pygame mixer is not initialized")
            self._change_state(PlayerState.ERROR)
            return False

        if not os.path.isfile(path):
            error = f"File not found: {path}"

            logger.error(error)

            self._notify_error(error)
            self._change_state(PlayerState.ERROR)

            return False

        try:
            self._stop_monitor()
            self._unload_current()

            self._path = path

            self.position = 0.0
            self.duration = 0.0
            self._last_position = 0.0

            self.error_message = None
            self.metadata = None

            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(
                self.volume / 100.0
            )

            self.duration = self._get_duration(path)
            self._change_state(PlayerState.LOADED)
            logger.info("Audio loaded successfully: %s | duration=%.2f",path,self.duration,)

            return True

        except Exception as e:

            logger.error("Failed to load audio: %s",path,)

            self._path = None
            self.duration = 0.0
            self.position = 0.0

            self._notify_error(e)
            self._change_state(PlayerState.ERROR)

            return False

    # =========================================================
    # DURATION
    # =========================================================

    def _get_duration(self, path):
        """
        Get audio duration.

        pygame.mixer.music does not provide duration directly,
        so we use pygame.mixer.Sound for supported formats.
        """

        try:
            sound = pygame.mixer.Sound(path)
            return float(sound.get_length())

        except Exception as e:

            logger.warning(
                "Could not determine duration: %s",
                e,
            )

            return 0.0

    # =========================================================
    # PLAY
    # =========================================================

    def play(self):
        """Start playback from beginning."""

        if not self._has_audio():
            logger.warning("No audio loaded")
            return False

        try:
            pygame.mixer.music.play(loops=-1 if self.loop else 0)

            self.position = 0.0
            self._last_position = 0.0

            self._start_monitor()
            self._change_state(PlayerState.PLAYING)
            return True

        except Exception as e:

            logger.error("Play error")

            self._notify_error(e)
            self._change_state(PlayerState.ERROR)

            return False

    # =========================================================
    # PAUSE
    # =========================================================

    def pause(self):
        """Pause playback."""

        if not self._has_audio():
            return False

        try:

            pygame.mixer.music.pause()
            self._stop_monitor()
            self._change_state(PlayerState.PAUSED)
            return True

        except Exception as e:
            logger.error("Pause error")
            self._notify_error(e)
            return False

    # =========================================================
    # RESUME
    # =========================================================

    def resume(self):
        """Resume paused playback."""

        if not self._has_audio():
            return False

        try:
            pygame.mixer.music.unpause()
            self._start_monitor()
            self._change_state(PlayerState.PLAYING)
            return True

        except Exception as e:
            logger.error("Resume error")
            self._notify_error(e)
            return False

    # =========================================================
    # STOP
    # =========================================================

    def stop(self):
        """Stop playback and reset position."""

        if not self._has_audio():
            return False

        try:

            pygame.mixer.music.stop()

            self._stop_monitor()

            self.position = 0.0
            self._last_position = 0.0
            self._change_state(PlayerState.STOPPED)
            return True

        except Exception as e:
            logger.error("Stop error")
            self._notify_error(e)
            return False

    # =========================================================
    # SEEK
    # =========================================================
    
    def seek(self, seconds: float) -> bool:
        if not self._has_audio():
            return False

        try:
            seconds = float(seconds)

            if self.duration > 0:
                seconds = max(
                    0.0,
                    min(seconds, self.duration)
                )
            else:
                seconds = max(0.0, seconds)

            was_playing = self.state == PlayerState.PLAYING
            was_paused = self.state == PlayerState.PAUSED

            if not was_playing and not was_paused:
                self.position = seconds
                self._last_position = seconds
                return True

            if was_paused:
                pygame.mixer.music.unpause()

            pygame.mixer.music.set_pos(seconds)

            self.position = seconds
            self._last_position = seconds

            if was_paused:
                pygame.mixer.music.pause()

            return True

        except Exception as e:
            logger.error("Seek error")
            self._notify_error(e)
            return False

    # =========================================================
    # VOLUME
    # =========================================================

    def set_volume(self, volume):
        """Set volume from 0 to 100."""

        try:
            volume = max(
                0,
                min(100, int(volume))
            )

            self.volume = volume

            if not self.muted:
                pygame.mixer.music.set_volume(
                    volume / 100.0
                )

            return True

        except Exception as e:

            logger.error("Volume error")

            self._notify_error(e)

            return False

    # =========================================================
    # MUTE
    # =========================================================

    def toggle_mute(self):
        """Toggle mute."""

        try:

            self.muted = not self.muted

            if self.muted:
                pygame.mixer.music.set_volume(0.0)

            else:
                pygame.mixer.music.set_volume(
                    self.volume / 100.0
                )

            return True

        except Exception as e:
            logger.error("Mute error")
            self._notify_error(e)
            return False

    # =========================================================
    # MONITOR
    # =========================================================

    def _start_monitor(self):

        if self._monitor_event is not None:
            return

        self._monitor_event = Clock.schedule_interval(
            self._monitor,
            0.1
        )

    def _stop_monitor(self):

        if self._monitor_event is not None:

            try:
                self._monitor_event.cancel()

            except Exception:
                pass

            self._monitor_event = None

    def _monitor(self, dt):
        if not self._has_audio():
            self._stop_monitor()
            return

        try:
            pos = pygame.mixer.music.get_pos()

            if pos < 0:
                if self.state == PlayerState.PLAYING:
                    self._handle_finished()
                return

            self.position = pos / 1000.0

            self._process_pygame_events()

        except Exception as e:
            logger.exception("Monitor error")

    # =========================================================
    # EVENTS
    # =========================================================

    def _process_pygame_events(self):
        for event in pygame.event.get():
            if event.type == self.END_EVENT:
                self._handle_finished()

    def _handle_finished(self):
        if self.state != PlayerState.PLAYING:
            return

        self._stop_monitor()
        self.position = self.duration
        self._change_state(PlayerState.FINISHED)
        if callable(self.on_finished):
            try:
                self.on_finished()
            except Exception:
                logger.exception("on_finished callback error")
    # =========================================================
    # RELEASE
    # =========================================================

    def release(self):
        self._stop_monitor()

        try:

            pygame.mixer.music.stop()

        except Exception:
            pass

        self._unload_current()

        self._path = None
        self.metadata = None

        self.duration = 0.0
        self.position = 0.0
        self._last_position = 0.0

        self.error_message = None

        self._change_state(
            PlayerState.EMPTY
        )

    def _unload_current(self):

        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

        try:
            pygame.mixer.music.unload()
        except Exception:
            pass

    # =========================================================
    # HELPERS
    # =========================================================

    def _has_audio(self):
        return (
            self._path is not None
            and self.state != PlayerState.ERROR
            and self._pygame_initialized
        )

    # =========================================================
    # STATES
    # =========================================================

    def is_loaded(self):
        return self.state == PlayerState.LOADED

    def is_playing(self):
        return self.state == PlayerState.PLAYING

    def is_paused(self):
        return self.state == PlayerState.PAUSED

    def is_finished(self):
        return self.state == PlayerState.FINISHED

    def is_stopped(self):
        return self.state == PlayerState.STOPPED

    def is_error(self):
        return self.state == PlayerState.ERROR

    # =========================================================
    # STATE CHANGE
    # =========================================================

    def _change_state(self, state):

        if self.state == state:
            return
        self.state = state
        if callable(self.on_state_changed):

            try:
                self.on_state_changed(state)

            except Exception:
                logger.error("State callback error")

    # =========================================================
    # ERROR
    # =========================================================

    def _notify_error(self, error):

        self.error_message = str(error)

        logger.error("Audio error: %s",error)

        if callable(self.on_error):

            try:
                self.on_error(error)

            except Exception:
                logger.error( "on_error callback error" )