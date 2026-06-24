import os
import threading
import time

import win32api
import win32con
import win32gui


class SplashScreen:
    def __init__(self, image_path, width, height):
        self.image_path = image_path
        self.width = width
        self.height = height
        self.hwnd = None
        self.class_name = "FlashCardSplashScreen"
        self._thread = None
        self._ready = threading.Event()
        self._close_requested = False

    def show(self):
        print("SPLASH: show called")
        print("SPLASH path:", self.image_path)
        print("SPLASH exists:", os.path.isfile(self.image_path))

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._ready.wait()

    def close(self):
        self._close_requested = True

        if self.hwnd:
            win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)

    def _run(self):
        hinst = win32api.GetModuleHandle(None)

        wc = win32gui.WNDCLASS()
        wc.hInstance = hinst
        wc.lpszClassName = self.class_name
        wc.lpfnWndProc = self._wnd_proc

        try:
            win32gui.RegisterClass(wc)
        except win32gui.error:
            pass
        
        image = win32gui.LoadImage(
            0,
            self.image_path,
            win32con.IMAGE_BITMAP,
            0,
            0,
            win32con.LR_LOADFROMFILE,
        )


        width = self.width
        height = self.height

        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # 1) اول پنجرهٔ اصلی
        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_TOOLWINDOW,
            self.class_name,
            "",
            win32con.WS_POPUP,
            x,
            y,
            width,
            height,
            0,
            0,
            hinst,
            None,
        )
        
        # 2) بعد تصویر به‌عنوان child پنجرهٔ اصلی
        self.image_control = win32gui.CreateWindowEx(
            0,
            "Static",
            "",
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.SS_BITMAP,
            0,
            0,
            width,
            height,
            self.hwnd,   # خیلی مهم: parent باید hwnd پنجرهٔ اصلی باشد
            0,
            hinst,
            None,
        )
        
        # 3) تصویر را به کنترل Static بده
        win32gui.SendMessage(
            self.image_control,
            win32con.STM_SETIMAGE,
            win32con.IMAGE_BITMAP,
            image,
        )

        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        win32gui.UpdateWindow(self.hwnd)
        
        print("SPLASH: window shown")

        self._ready.set()

        while not self._close_requested:
            win32gui.PumpWaitingMessages()
            time.sleep(0.01)

        if self.hwnd:
            win32gui.DestroyWindow(self.hwnd)
            self.hwnd = None

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)