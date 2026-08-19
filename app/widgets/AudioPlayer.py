from enum import Enum
import os
import time

import pygame
from kivy.clock import Clock

from app.cmn.logger import logger


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
        self._position_base = 0.0
        self._position_started_at = None

        self._finish_handled = False

        self._last_busy = False

        self._init_mixer()

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
            logger.exception(
                "Failed to initialize pygame mixer"
            )

            self._notify_error(e)
            self._change_state(PlayerState.ERROR)

    def load(self, path):
        """Load a new audio file."""

        if not self._pygame_initialized:
            self._notify_error(
                "Pygame mixer is not initialized"
            )
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

            self._clear_end_events()

            self._unload_current()

            self._path = path

            self.position = 0.0
            self.duration = 0.0
            self._last_position = 0.0

            self._position_base = 0.0
            self._position_started_at = None

            self._finish_handled = False
            self._last_busy = False

            self.error_message = None
            self.metadata = None

            pygame.mixer.music.load(path)

            pygame.mixer.music.set_volume(
                self.volume / 100.0
            )

            self.duration = self._get_duration(path)

            self._change_state(PlayerState.LOADED)

            logger.info(
                "Audio loaded successfully: %s | duration=%.2f",
                path,
                self.duration,
            )

            return True

        except Exception as e:

            logger.exception(
                "Failed to load audio: %s",
                path,
            )

            self._path = None
            self.duration = 0.0
            self.position = 0.0

            self._position_base = 0.0
            self._position_started_at = None

            self._finish_handled = False
            self._last_busy = False

            self._notify_error(e)
            self._change_state(PlayerState.ERROR)

            return False

    def _get_duration(self, path):
        """
        Get audio duration.

        pygame.mixer.music does not provide duration directly,
        so pygame.mixer.Sound is used.
        """

        try:
            sound = pygame.mixer.Sound(path)

            duration = float(
                sound.get_length()
            )

            del sound

            return duration

        except Exception as e:

            logger.warning(
                "Could not determine duration: %s",
                e,
            )

            return 0.0

    def play(self):
        """Start playback from beginning."""

        if not self._has_audio():
            logger.warning("No audio loaded")
            return False

        try:

            self._clear_end_events()

            self._finish_handled = False

            pygame.mixer.music.play(
                -1 if self.loop else 0,
                0.0,
            )

            self.position = 0.0
            self._last_position = 0.0

            self._position_base = 0.0
            self._position_started_at = time.monotonic()

            self._last_busy = True

            self._start_monitor()

            self._change_state(
                PlayerState.PLAYING
            )

            logger.debug(
                "Playback started: %s",
                self._path,
            )

            return True

        except Exception as e:

            logger.exception("Play error")

            self._notify_error(e)
            self._change_state(
                PlayerState.ERROR
            )

            return False

    def pause(self):
        if not self._has_audio():
            return False

        try:

            if self.state == PlayerState.PLAYING:
                self._update_position_from_clock()

            pygame.mixer.music.pause()

            self._position_started_at = None

            self._last_busy = False

            self._stop_monitor()

            self._change_state(
                PlayerState.PAUSED
            )

            return True

        except Exception as e:

            logger.exception(
                "Pause error"
            )

            self._notify_error(e)

            return False

    def resume(self):
        if not self._has_audio():
            return False

        try:

            self._clear_end_events()

            self._finish_handled = False

            pygame.mixer.music.unpause()

            self._position_base = self.position
            self._position_started_at = time.monotonic()

            self._last_busy = True

            self._start_monitor()

            self._change_state(
                PlayerState.PLAYING
            )

            return True

        except Exception as e:

            logger.exception(
                "Resume error"
            )

            self._notify_error(e)

            return False

    def stop(self):
        """Stop playback and reset position."""

        if not self._has_audio():
            return False

        try:

            pygame.mixer.music.stop()

            self._last_busy = False

            self._clear_end_events()

            self._stop_monitor()

            self.position = 0.0
            self._last_position = 0.0

            self._position_base = 0.0
            self._position_started_at = None

            self._finish_handled = False

            self._change_state(
                PlayerState.STOPPED
            )

            return True

        except Exception as e:

            logger.exception(
                "Stop error"
            )

            self._notify_error(e)

            return False

    def seek(self, seconds: float) -> bool:

        if not self._has_audio():
            return False

        try:

            seconds = float(seconds)

            if self.duration > 0:
                seconds = max(
                    0.0,
                    min(
                        seconds,
                        self.duration
                    )
                )
            else:
                seconds = max(
                    0.0,
                    seconds
                )

            was_playing = (
                self.state == PlayerState.PLAYING
            )

            was_paused = (
                self.state == PlayerState.PAUSED
            )

            if not was_playing and not was_paused:

                self.position = seconds
                self._last_position = seconds

                self._position_base = seconds
                self._position_started_at = None

                return True

            self._clear_end_events()

            self._finish_handled = False

            if (
                self.duration > 0
                and seconds >= self.duration
            ):
                seconds = max(
                    0.0,
                    self.duration - 0.01
                )

            pygame.mixer.music.play(
                -1 if self.loop else 0,
                seconds,
            )

            self.position = seconds
            self._last_position = seconds
            self._position_base = seconds

            if was_playing:

                self._position_started_at = (
                    time.monotonic()
                )

                self._last_busy = True

            else:

                pygame.mixer.music.pause()

                self._position_started_at = None
                self._position_base = seconds

                self._last_busy = False

            return True

        except NotImplementedError:

            logger.exception(
                "Seek is not supported for this audio format"
            )

            self._notify_error(
                "Seeking is not supported for this audio format"
            )

            return False

        except Exception as e:

            logger.exception(
                "Seek error"
            )

            self._notify_error(e)

            return False

    def set_volume(self, volume):
        """Set volume from 0 to 100."""

        try:

            volume = max(
                0,
                min(
                    100,
                    int(volume)
                )
            )

            self.volume = volume

            if not self.muted:

                pygame.mixer.music.set_volume(
                    volume / 100.0
                )

            return True

        except Exception as e:

            logger.exception(
                "Volume error"
            )

            self._notify_error(e)

            return False

    def toggle_mute(self):
        """Toggle mute."""

        try:

            self.muted = not self.muted

            if self.muted:

                pygame.mixer.music.set_volume(
                    0.0
                )

            else:

                pygame.mixer.music.set_volume(
                    self.volume / 100.0
                )

            return True

        except Exception as e:

            logger.exception(
                "Mute error"
            )

            self._notify_error(e)

            return False

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

            if self.state == PlayerState.PLAYING:

                self._update_position_from_clock()

            self._process_pygame_events()

            #

            #

            #

            #

            if (
                self.state == PlayerState.PLAYING
                and not self.loop
                and self.duration > 0
            ):

                busy = pygame.mixer.music.get_busy()

                if (
                    self._last_busy
                    and not busy
                    and self.position >= self.duration - 0.15
                ):
                    logger.debug(
                        "Playback end detected by monitor: "
                        "position=%.3f duration=%.3f",
                        self.position,
                        self.duration,
                    )

                    self._handle_finished()

                self._last_busy = busy

        except Exception:

            logger.exception(
                "Monitor error"
            )

    def _update_position_from_clock(self):

        if self._position_started_at is None:
            return

        elapsed = (
            time.monotonic()
            - self._position_started_at
        )

        self.position = (
            self._position_base
            + elapsed
        )

        if self.duration > 0:

            self.position = min(
                self.position,
                self.duration
            )

    def _clear_end_events(self):
        """
        Remove stale END_EVENTs from pygame event queue.
        """

        try:

            pygame.event.clear(
                self.END_EVENT
            )

        except Exception:

            logger.exception(
                "Failed to clear pygame END_EVENTs"
            )

    def _process_pygame_events(self):

        try:

            events = pygame.event.get(
                self.END_EVENT
            )

            if not events:
                return

            for event in events:

                if self.state != PlayerState.PLAYING:
                    continue

                logger.debug(
                    "Received pygame END_EVENT"
                )

                #

                #
                self._handle_finished()

        except Exception:

            logger.exception(
                "Error processing pygame events"
            )

    def _handle_finished(self):

        if self.state != PlayerState.PLAYING:
            return

        if self._finish_handled:
            return

        self._finish_handled = True

        self._last_busy = False

        self._stop_monitor()

        if self.duration > 0:

            self.position = self.duration
            self._last_position = self.duration
            self._position_base = self.duration

        self._position_started_at = None

        self._change_state(
            PlayerState.FINISHED
        )

        logger.info(
            "Audio playback finished: %s",
            self._path,
        )

        if callable(self.on_finished):

            try:
                self.on_finished()

            except Exception:

                logger.exception(
                    "on_finished callback error"
                )

    def release(self):

        self._stop_monitor()

        try:
            pygame.mixer.music.stop()

        except Exception:
            pass

        self._last_busy = False

        self._clear_end_events()

        self._unload_current()

        self._path = None
        self.metadata = None

        self.duration = 0.0
        self.position = 0.0
        self._last_position = 0.0

        self._position_base = 0.0
        self._position_started_at = None

        self._finish_handled = False

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

    def _has_audio(self):

        return (
            self._path is not None
            and self.state != PlayerState.ERROR
            and self._pygame_initialized
        )

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

    def _change_state(self, state):

        if self.state == state:
            return

        self.state = state

        if callable(self.on_state_changed):

            try:
                self.on_state_changed(state)

            except Exception:

                logger.exception(
                    "State callback error"
                )

    def _notify_error(self, error):

        self.error_message = str(error)

        logger.error(
            "Audio error: %s",
            error
        )

        if callable(self.on_error):

            try:
                self.on_error(error)

            except Exception:

                logger.exception(
                    "on_error callback error"
                )
