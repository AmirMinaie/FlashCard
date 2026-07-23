from enum import Enum
from ffpyplayer.player import MediaPlayer
from kivy.clock import Clock
import traceback
import os

class PlayerState(Enum):
    EMPTY = "empty"
    LOADED = "loaded"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    FINISHED = "finished"
    ERROR = "error"

class AudioPlayer:

    def __init__(self):
        # MediaPlayer
        self._player = None
        self.metadata = None

        # File Information
        self._path = None

        # Player State
        self.state = PlayerState.EMPTY

        # Settings
        self.volume = 100
        self.loop = False
        self.muted = False
        self.error_message = None

        # Media Information
        self.duration = 0.0
        self.position = 0.0

        # Callbacks
        self.on_finished = None
        self.on_error = None
        self.on_state_changed = None

        # Internal
        self._monitor_event = None

    # ==========================
    # Public Methods
    # ==========================

    def load(self, path):
        self.release()

        if not os.path.isfile(path):
            self.error_message = f"File not found: {path}"
            self._notify_error(self.error_message)
            self._change_state(PlayerState.ERROR)
            return False

        self._path = path

        try:
            self._create_player()
            self._change_state(PlayerState.LOADED)
            return True

        except Exception as e:
            traceback.print_exc()
            self._notify_error(e)
            self._change_state(PlayerState.ERROR)
            return False

    def play(self) -> bool:
        return self.resume()

    def pause(self) -> bool:
        """
        Pause playback.
        Returns:
            bool: True if successful.
        """

        if self._player is None:
            return False

        try:
            self._player.set_pause(True)
            self._change_state(PlayerState.PAUSED)
            return True

        except Exception as e:
            self._notify_error(e)
            self._change_state(PlayerState.ERROR)
            return False

    def resume(self) -> bool:
        """
        Resume playback.
        Returns:
            bool: True if successful.
        """

        if self._player is None:
            return False

        if self.state == PlayerState.FINISHED or self.state == PlayerState.STOPPED:
            try:
                self._player.seek(pts=0, relative=False, accurate=True)
                self.position = 0
            except:
                pass

        try:
            self._player.set_pause(False)

            self._start_monitor()

            self._change_state(PlayerState.PLAYING)
            return True

        except Exception as e:
            self._notify_error(e)
            self._change_state(PlayerState.ERROR)
            return False

    def stop(self) -> bool:
        """
        Stop playback and seek to the beginning.
        Returns: bool: True if stopped successfully.
        """

        if self._player is None:
            return False

        try:
            self._player.set_pause(True)

            try:
                self._player.seek( pts=0, relative=False, accurate=True )
            except:
                pass

            self._stop_monitor()

            self.position = 0.0

            self._change_state(PlayerState.STOPPED)

            return True

        except Exception as e:
            self._notify_error(e)
            self._change_state(PlayerState.ERROR)
            return False

    def release(self):
        """
        Release all player resources.
        """
        self._stop_monitor()
        if self._player is not None:
            try:
                self._player.close_player()
            except Exception as e:
                self._notify_error(e)
            finally:
                self._player = None

        self._path = None
        self.position = 0.0
        self.duration = 0.0
        self.muted = False


        self._change_state(PlayerState.EMPTY)

    def seek(self, seconds):
        if self._player is None:
            return False

        try:
            self._player.seek(pts=seconds, relative=False, accurate=True)
            self.position = seconds
            return True
        except Exception as e:
            self._notify_error(e)
            return False

    def set_volume(self, volume: int) -> bool:
        """
        Set player volume.

        Args:
            volume: Volume level (0-100)

        Returns:
            bool: True if successful.
        """

        volume = max(0, min(100, int(volume)))
        self.volume = volume

        if self._player is None:
            return True

        try:
            self._player.set_volume(volume / 100)
            return True

        except Exception as e:
            self._notify_error(e)
            return False

    def toggle_mute(self) -> bool:
        if self._player is None:
            return False

        try:
            self.muted = not self.muted
            self._player.set_mute(self.muted)
            return True

        except Exception as e:
            self._notify_error(e)
            return False

    # ==========================
    # Getters
    # ==========================

    def is_loaded(self):
        return self.state == PlayerState.LOADED

    def is_playing(self):
        return self.state == PlayerState.PLAYING

    def is_paused(self):
        return self.state == PlayerState.PAUSED

    def is_finished(self):
        return self.state == PlayerState.FINISHED

    # ==========================
    # Internal Methods
    # ==========================
    def _create_player(self):
        """Create MediaPlayer instance."""
        self._player = MediaPlayer(
            self._path,
            ff_opts={
                "paused": True,
                "vn": True, 
                "sn": True, 
            })

        self.duration = 0.0
        self._wait_for_duration(attempt=3)

        self._player.set_volume(self.volume / 100)

    def _wait_for_duration(self, attempt=0):
        self.metadata = self._player.get_metadata()

        if self.metadata and self.metadata.get('duration'):
            self.duration = float(self.metadata['duration'])
            if self.duration > 0:
                return

        if attempt < 20:
            Clock.schedule_once(
                lambda dt: self._wait_for_duration(attempt + 1),
                0.05
            )
        else:
            self.duration = 0.0

    def _change_state(self, state):
        if self.state == state:
            return

        self.state = state

        if callable(self.on_state_changed):
            self.on_state_changed(state)

    def _start_monitor(self):
        print("START MONITOR CALLED")

        if self._monitor_event is None:
            self._monitor_event = Clock.schedule_interval(
                self._monitor,
                0.1
            )

    def _stop_monitor(self):
        if self._monitor_event is not None:
            self._monitor_event.cancel()
            self._monitor_event = None

    def _monitor(self, dt):
        """
        Monitor playback status.
        """
        if self._player is None:
            return

        try:
            current_pos = self._player.get_pts()

            if current_pos is None:
                return

            if current_pos is not None:
                self.position = self._player.get_pts()
                print(f"Position: {self.position}")
                print(f"Duration: {self.duration}")

                if self.duration > 0 and self.position >= self.duration - 0.1:
                    print("EOF DETECTED")
                    self._stop_monitor()
                    self._player.set_pause(True)

                    if self.loop:
                        self._player.seek(pts=0, relative=False, accurate=True)
                        self._player.set_pause(False)
                        self.position = 0
                        self._start_monitor()
                        return

                    self.position = 0
                    self._change_state(PlayerState.FINISHED)

                    if callable(self.on_finished):
                        self.on_finished()

            self._player.get_frame()

        except Exception as e:
            self._notify_error(e)
            self._change_state(PlayerState.ERROR)
            self.release()

    def _notify_finished(self):
        """Called when playback finishes."""
        if callable(self.on_finished):
            self.on_finished()

    def _notify_error(self, error):
        print(f"[AudioPlayer Error] {error}")
        import traceback
        traceback.print_exc()
        if callable(self.on_error):
            self.on_error(error)