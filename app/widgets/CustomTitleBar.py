# widgets/CustomTitleBar.py

from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.uix.button import MDIconButton
from kivy.uix.image import Image
import win32api
import win32con
import win32gui
from pathlib import Path
from cmn.logger import logger


Builder.load_string("""

<CustomTitleBar>:
    icon_path: app.title_icon
    title_text: app.title_text
    

    size_hint_y: None
    height: dp(45)

    padding: dp(10), 0
    spacing: dp(8)

    canvas.after:
        Color:
            rgba: 1, 1, 1, 0.15

        Line:
            width: dp(1)
            points: self.x, self.y, self.right, self.y


    Image:
        id: app_icon
        source: root.icon_path
        size_hint: None, None
        size: dp(30), dp(30)
        pos_hint: {"center_y": .5}


    MDLabel:
        id: title_label
        text: root.title_text
        bold: True
        size_hint_x: None
        width: dp(150)
        valign: "center"


    Widget:


    MDIconButton:
        id: btn_min
        icon: "minus"
        size_hint: None, None
        size: dp(34), dp(34)
        pos_hint: {"center_y": .5}

        on_release:
            app.minimize_window()

    MDIconButton:
        id: btn_max
        icon: "window-maximize"
        size_hint: None, None
        size: dp(34), dp(34)
        pos_hint: {"center_y": .5}
        on_release:
            app.toggle_maximize()

    MDIconButton:
        id: btn_close
        icon: "close"
        size_hint: None, None
        size: dp(34), dp(34)
        pos_hint: {"center_y": .5}

        on_release:
            app.close_app()

""")


class CustomTitleBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dragging = False
        self._offset_x = 0
        self._offset_y = 0
        self.hwnd = None

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        
        # بررسی اینکه روی دکمه‌ها کلیک نشده باشد
        for child in self.children:
            if isinstance(child, MDIconButton) and child.collide_point(*touch.pos):
                return super().on_touch_down(touch)
        
        # گرفتن handle پنجره
        if not self.hwnd:
            self.hwnd = win32gui.GetForegroundWindow()
        
        if self.hwnd:
            try:
                self._dragging = True
                
                mouse_x, mouse_y = win32api.GetCursorPos()
                rect = win32gui.GetWindowRect(self.hwnd)
                self._offset_x = mouse_x - rect[0]
                self._offset_y = mouse_y - rect[1]
                
                win32gui.SetCapture(self.hwnd)
                return True
                
            except Exception as e:
                logger.info(f"Error in touch_down: {e}")
                self._dragging = False
        
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._dragging and self.hwnd:
            try:
                mouse_x, mouse_y = win32api.GetCursorPos()
                
                new_x = mouse_x - self._offset_x
                new_y = mouse_y - self._offset_y
                
                win32gui.SetWindowPos(
                    self.hwnd, 
                    win32con.HWND_TOPMOST,
                    new_x, new_y, 
                    0, 0,
                    win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
                )
                
                return True
                
            except Exception as e:
                logger.info(f"Error in touch_move: {e}")
                self._dragging = False
        
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._dragging:
            self._dragging = False
            if self.hwnd:
                try:
                    win32gui.ReleaseCapture()
                except:
                    pass
            return True
        
        return super().on_touch_up(touch)