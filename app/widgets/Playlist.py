#                Playlist:
#                    id: playlist_widget
#                    songs: root.get_list_songs()
#                    size_hint_y: None
#                    height: dp(250)  # کاهش ارتفاع Playlist
#                    padding: ["10dp", "0dp"]  # padding کمتر
#                    spacing: "5dp"  # spacing داخلی کمتر
#                    time_slider_enabled: True
#                    volume_slider_enabled: True


from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider
from ffpyplayer.player import MediaPlayer
from kivy.clock import Clock
from kivy.lang import Builder
import time
from cmn.resource_helper import resource_path
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
import os

Builder.load_file(resource_path("app" , "widgets","Playlist.kv"))


class Playlist(MDBoxLayout):
    current_song = StringProperty('unknow')
    current_time = StringProperty("00:00")
    total_time = StringProperty("00:00")
    progress_value = NumericProperty(0)
    is_playing = BooleanProperty(False)
    songs = ListProperty()
    volume_level = NumericProperty(50)
    fixed_height = NumericProperty(300)
    time_slider_enabled = BooleanProperty(True)
    volume_slider_enabled = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sound = None
        self.clock_event = None
        self.current_index = 0
        self.is_seeking = False
        self.sound_length = 0
        self.last_update_time = 0
        self.height = self.fixed_height
        self.last_volume = 50

    def load_song(self, filepath):
        if self.sound:
            self.sound.set_pause(True)
            if self.clock_event:
                self.clock_event.cancel()
                self.clock_event = None
        
        try:
            self.sound = MediaPlayer(resource_path('files', filepath.filePath))
            time.sleep(0.2)  # کمی بیشتر صبر کن
            
            # دریافت طول آهنگ
            metadata = self.sound.get_metadata()
            if metadata and 'duration' in metadata:
                self.sound_length = metadata['duration']
            else:
                # اگر نتوانستیم طول آهنگ را بگیریم، یک مقدار پیش‌فرض قرار می‌دهیم
                self.sound_length = 0
            
            if self.sound:
                self.current_song = filepath.fileName
                self.total_time = self.format_time(self.sound_length) if self.sound_length > 0 else "00:00"
                self.current_time = "00:00"
                self.progress_value = 0
                self.sound.set_volume(self.volume_level / 100.0)
                
                # اگر قبلاً در حال پخش بودیم، ادامه بده
                if self.is_playing:
                    self.start_progress_updater()
                    
        except Exception as e:
            print(f"Error loading song: {e}")

    def toggle_play(self):
        """شروع/توقف پخش"""
        if not self.sound:
            if self.songs:
                self.load_song(self.songs[0])
            else:
                return
        
        if self.is_playing:
            # توقف پخش
            self.is_playing = False
            self.sound.set_pause(True)
            if self.clock_event:
                self.clock_event.cancel()
                self.clock_event = None
        else:
            # شروع پخش
            self.is_playing = True
            self.sound.set_pause(False)
            
            # اگر آهنگ تمام شده بود، از ابتدا شروع کن
            if self.progress_value >= 99.9:
                self.sound.seek(0)
                self.progress_value = 0
                self.current_time = "00:00"
            
            self.start_progress_updater()
    
    def start_progress_updater(self):
        """شروع آپدیت موقعیت پخش"""
        if self.clock_event:
            self.clock_event.cancel()
        
        self.clock_event = Clock.schedule_interval(self.update_progress, 0.1)
    
    def update_progress(self, dt):
        """آپدیت موقعیت پخش"""
        if self.sound and self.is_playing and not self.is_seeking:
            try:
                current_pos = self.sound.get_pts()
                if current_pos is None:
                    return
                    
                # آپدیت نمایش زمان
                self.current_time = self.format_time(current_pos)
                
                # آپدیت اسلایدر
                if self.sound_length > 0:
                    new_progress = (current_pos / self.sound_length) * 100
                    # فقط اگر تغییر قابل توجهی داشت آپدیت کن
                    if abs(new_progress - self.progress_value) > 0.1:
                        self.progress_value = new_progress
                    
                    # بررسی پایان آهنگ (با حاشیه خطا)
                    if current_pos >= self.sound_length - 0.3:
                        self.on_song_end()
                        
            except Exception as e:
                print(f"Error updating progress: {e}")

    def on_slider_value(self, slider, value):
        """هنگام تغییر مقدار اسلایدر"""
        # این تابع وقتی که کاربر اسلایدر را می‌کشد صدا زده می‌شود
        if not self.sound or self.sound_length <= 0:
            return
        
        # فقط نمایش زمان را آپدیت کن، seek نکن
        if slider.active:
            self.is_seeking = True
            new_position = (value / 100.0) * self.sound_length
            self.current_time = self.format_time(new_position)

    def on_touch_up(self, touch):
        """هنگام رها کردن لماس"""
        # اگر کاربر در حال کشیدن اسلایدر بود
        if self.is_seeking:
            self.is_seeking = False
            
            # seek به موقعیت جدید
            if self.sound and self.sound_length > 0:
                try:
                    new_position = (self.ids.progress_slider.value / 100.0) * self.sound_length
                    self.sound.seek(new_position, relative=False, accurate=True)
                    
                    # آپدیت زمان جاری
                    self.current_time = self.format_time(new_position)
                    
                    # اگر در حال پخش بودیم، تایمر را ریستارت کن
                    if self.is_playing and self.clock_event:
                        self.clock_event.cancel()
                        self.start_progress_updater()
                        
                except Exception as e:
                    print(f"Error seeking: {e}")
        
        return super().on_touch_up(touch)
    
    def set_volume(self, value):
        """تنظیم حجم صدا"""
        self.volume_level = value
        if self.sound:
            try:
                self.sound.set_volume(self.volume_level / 100.0)
            except:
                pass
    
    def on_song_end(self):
        """وقتی آهنگ تمام می‌شود"""
        self.is_playing = False
        self.current_time = self.total_time
        self.progress_value = 100
        
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
        
        # بعد از کمی تاخیر، آهنگ بعدی را پخش کن
        Clock.schedule_once(lambda dt: self.next_song(), 0.5)
    
    def format_time(self, seconds):
        """فرمت زمان به MM:SS"""
        if seconds is None or seconds < 0:
            seconds = 0
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def prev_song(self):
        """آهنگ قبلی"""
        if self.songs and len(self.songs) > 0:
            self.current_index = (self.current_index - 1) % len(self.songs)
            self.load_song(self.songs[self.current_index])
    
    def next_song(self):
        """آهنگ بعدی"""
        if self.songs and len(self.songs) > 0:
            self.current_index = (self.current_index + 1) % len(self.songs)
            self.load_song(self.songs[self.current_index])
    
    def toggle_mute(self):
        """موت کردن"""
        if self.volume_level > 0:
            self.last_volume = self.volume_level
            self.set_volume(0)
        else:
            self.set_volume(self.last_volume)
    
    def on_stop(self):
        """تمیزکاری هنگام توقف"""
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
        
        if self.sound:
            try:
                self.sound.set_pause(True)
                self.sound.close_player()
                self.sound = None
                self.songs = []

            except:
                pass
    
    # متدهای جدید برای کنترل نمایش اسلایدرها
    def show_time_slider(self, show=True):
        """نمایش/عدم نمایش اسلایدر زمان"""
        self.time_slider_enabled = show
    
    def show_volume_slider(self, show=True):
        """نمایش/عدم نمایش اسلایدر صدا"""
        self.volume_slider_enabled = show
    
    def toggle_time_slider(self):
        """تغییر وضعیت نمایش اسلایدر زمان"""
        self.time_slider_enabled = not self.time_slider_enabled
    
    def toggle_volume_slider(self):
        """تغییر وضعیت نمایش اسلایدر صدا"""
        self.volume_slider_enabled = not self.volume_slider_enabled