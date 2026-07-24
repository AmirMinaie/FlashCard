# audio_player.py - نسخه نهایی با راه‌حل اساسی
from enum import Enum
from ffpyplayer.player import MediaPlayer
from kivy.clock import Clock
import logging
import os
import gc

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        self._player = None
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
        self._eof_detected = False

    def load(self, path):
        """Load a new audio file"""
        logger.debug(f"load called with path: {path}")
        
        if not os.path.isfile(path):
            self.error_message = f"File not found: {path}"
            logger.error(self.error_message)
            self._notify_error(self.error_message)
            self._change_state(PlayerState.ERROR)
            return False

        # **راه‌حل: همیشه release کامل و ایجاد مجدد بدون sleep**
        
        # بستن مانیتور
        self._stop_monitor()
        
        # بستن پلیر قدیمی
        if self._player is not None:
            try:
                self._player.set_pause(True)
                self._player.close_player()
            except Exception as e:
                logger.exception("Monitor error")
                self._notify_error(e)
                self._change_state(PlayerState.ERROR)
                self._stop_monitor()
                
            self._player = None
        
        # پاکسازی
        gc.collect()
        
        # تنظیم مسیر جدید
        self._path = path
        self.position = 0.0
        self.duration = 0.0
        self._eof_detected = False
        self.error_message = None
        
        try:
            # ساخت پلیر جدید - بدون sleep
            ff_opts = {
                "paused": True,
                "vn": True,
                "sn": True,
            }
            
            self._player = MediaPlayer(path, ff_opts=ff_opts)
            self._player.set_volume(self.volume / 100.0)
            
            # گرفتن duration به صورت async با Clock
            Clock.schedule_once(lambda dt: self._get_duration_async(0), 0.05)
            
            self._change_state(PlayerState.LOADED)
            logger.info(f"Successfully loaded: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create player: {e}")
            self.error_message = str(e)
            self._notify_error(e)
            self._change_state(PlayerState.ERROR)
            return False

    def _get_duration_async(self, attempt):
        """دریافت duration به صورت async"""
        if self._player is None or attempt >= 15:
            if attempt >= 15:
                logger.warning("Could not get duration")
            return
        
        try:
            metadata = self._player.get_metadata()
            if metadata and 'duration' in metadata and metadata['duration'] is not None:
                self.duration = float(metadata['duration'])
                self.metadata = metadata
                logger.info(f"Duration: {self.duration}s")
                return
        except:
            pass
        
        # تلاش مجدد
        Clock.schedule_once(lambda dt: self._get_duration_async(attempt + 1), 0.05)

    def play(self) -> bool:
        logger.debug("play called")
        
        if self._player is None:
            logger.warning("No player")
            return False
        
        try:
            # اگر finished یا stopped هست، seek به 0
            if self.state in [PlayerState.FINISHED, PlayerState.STOPPED]:
                self._player.seek(pts=0, relative=False, accurate=True)
                self.position = 0
                self._eof_detected = False
            
            # unpause
            self._player.set_pause(False)
            self._start_monitor()
            self._change_state(PlayerState.PLAYING)
            return True
            
        except Exception as e:
            logger.error(f"Play error: {e}")
            self._notify_error(e)
            self._change_state(PlayerState.ERROR)
            return False

    def pause(self) -> bool:
        logger.debug("pause called")
        
        if self._player is None:
            return False
        
        try:
            self._player.set_pause(True)
            self._stop_monitor()
            self._change_state(PlayerState.PAUSED)
            return True
        except Exception as e:
            logger.error(f"Pause error: {e}")
            return False

    def resume(self) -> bool:
        logger.debug("resume called")
        
        if self._player is None:
            return False
        
        try:
            self._player.set_pause(False)
            self._start_monitor()
            self._change_state(PlayerState.PLAYING)
            return True
        except Exception as e:
            logger.error(f"Resume error: {e}")
            return False

    def stop(self) -> bool:
        logger.debug("stop called")
        
        if self._player is None:
            return False
        
        try:
            self._stop_monitor()
            self._player.set_pause(True)
            
            try:
                self._player.seek(pts=0, relative=False, accurate=True)
            except:
                pass
            
            self.position = 0.0
            self._eof_detected = False
            self._change_state(PlayerState.STOPPED)
            return True
        except Exception as e:
            logger.error(f"Stop error: {e}")
            return False

    def seek(self, seconds: float) -> bool:
        if self._player is None:
            return False
        
        try:
            if self.duration > 0:
                seconds = max(0.0, min(float(seconds), self.duration))
            
            self._player.seek(pts=seconds, relative=False, accurate=True)
            self.position = seconds
            self._eof_detected = False
            return True
        except:
            return False

    def release(self):
        self._stop_monitor()
        if self._player:
            try:
                self._player.set_pause(True)
                self._player.close_player()
            except:
                pass
            self._player = None
        self._path = None
        self.metadata = None
        self.duration = 0.0
        self.position = 0.0
        self._change_state(PlayerState.EMPTY)

    def set_volume(self, volume: int) -> bool:
        volume = max(0, min(100, int(volume)))
        self.volume = volume
        if self._player:
            try:
                self._player.set_volume(volume / 100.0)
            except:
                pass
        return True

    def toggle_mute(self) -> bool:
        if self._player is None:
            return False
        self.muted = not self.muted
        try:
            self._player.set_mute(self.muted)
        except:
            pass
        return True

    def is_loaded(self): return self.state == PlayerState.LOADED
    def is_playing(self): return self.state == PlayerState.PLAYING
    def is_paused(self): return self.state == PlayerState.PAUSED
    def is_finished(self): return self.state == PlayerState.FINISHED
    def is_stopped(self): return self.state == PlayerState.STOPPED
    def is_error(self): return self.state == PlayerState.ERROR

    def _change_state(self, state):
        if self.state == state:
            return
        old = self.state
        self.state = state
        logger.debug(f"State: {old.value} -> {state.value}")
        if callable(self.on_state_changed):
            try:
                self.on_state_changed(state)
            except:
                pass

    def _start_monitor(self):
        if self._monitor_event is not None:
            return
        self._monitor_event = Clock.schedule_interval(self._monitor, 0.1)

    def _stop_monitor(self):
        if self._monitor_event is not None:
            try:
                self._monitor_event.cancel()
            except:
                pass
            self._monitor_event = None

    def _monitor(self, dt):
        if self._player is None:
            self._stop_monitor()
            return
        
        try:
            pos = self._player.get_pts()
            if pos is not None:
                self.position = pos
                if self.duration > 0 and self.position >= self.duration - 0.2:
                    if not self._eof_detected:
                        self._handle_eof()
                        return
            
            self._player.get_frame(force_refresh=False)
        except:
            pass

    def _handle_eof(self):
        self._eof_detected = True
        if self.loop:
            try:
                self._player.seek(pts=0, relative=False, accurate=True)
                self._player.set_pause(False)
                self.position = 0
                self._eof_detected = False
            except:
                self._stop_monitor()
                self._change_state(PlayerState.ERROR)
        else:
            self._stop_monitor()
            try:
                self._player.set_pause(True)
            except:
                pass
            self.position = 0
            self._change_state(PlayerState.FINISHED)
            if callable(self.on_finished):
                try:
                    self.on_finished()
                except:
                    pass

    def _notify_error(self, error):
        self.error_message = str(error)
        logger.error(f"Error: {error}")
        if callable(self.on_error):
            try:
                self.on_error(error)
            except:
                pass