import ctypes
import win32con
import win32gui
import win32api
from cmn.logger import logger

class WindowManager:
    _hwnd = None

    @classmethod
    def initialize(cls):
        cls._hwnd = win32gui.GetActiveWindow()

        print("HWND:", cls._hwnd)

    @classmethod
    def hwnd(cls):
        if cls._hwnd is None:
            raise RuntimeError("WindowManager.initialize() has not been called.")
        return cls._hwnd

    @classmethod
    def maximize(cls):
        print("maximize")
        win32gui.ShowWindow(cls.hwnd(), win32con.SW_MAXIMIZE)


    @classmethod
    def restore(cls):
        print("restore")
        win32gui.ShowWindow(cls.hwnd(), win32con.SW_RESTORE)


    @classmethod
    def is_maximized(cls):
        print("IsZoomed:", ctypes.windll.user32.IsZoomed(cls.hwnd()))
        return bool(ctypes.windll.user32.IsZoomed(cls.hwnd()))


    @classmethod
    def set_window_icon(cls, icon_path):
        try:
            hwnd = cls._hwnd

            icon_small = win32gui.LoadImage( 0, icon_path, win32con.IMAGE_ICON, 16, 16, win32con.LR_LOADFROMFILE,)

            icon_big = win32gui.LoadImage( 0, icon_path, win32con.IMAGE_ICON, 32, 32, win32con.LR_LOADFROMFILE, )

            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, icon_small)
            win32gui.SendMessage( hwnd, win32con.WM_SETICON, win32con.ICON_BIG, icon_big, )
            ctypes.windll.user32.SetClassLongW( hwnd, -14,   icon_small or icon_big, )
    
            logger.info("Window icon set successfully")
        except Exception as e:
            logger.error(f"Error setting window icon: {e} : {win32api.GetLastError()}")