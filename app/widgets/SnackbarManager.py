from kivymd.uix.button import MDIconButton
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.snackbar import ( MDSnackbar, MDSnackbarActionButton )
from widgets.MDLabelA import MDLabelA

class Msg_type:
    success =  "success"
    error =  "error"
    warning =  "warning"
    info =  "info"

class SnackbarManager:

    _instance = None

    MAX_SNACKBARS = 3
    OFFSET_Y = 70

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

            cls._instance.active_snackbars = []

        return cls._instance

    def show_snackbar( self, message, duration=3, msg_type= Msg_type.info ):

        if len(self.active_snackbars) >= self.MAX_SNACKBARS:
            old = self.active_snackbars.pop(0)
            old.dismiss()

        colors = {
            "success":(0.2, 0.7, 0.3, 1),
            "error":(0.9, 0.2, 0.2, 1),
            "warning":(1, 0.6, 0.1, 1),
            "info":(0.15, 0.15, 0.15, 1)
        }

        index = len(self.active_snackbars)

        y_position = dp(24) + dp(
            self.OFFSET_Y * index
        )

        snackbar = MDSnackbar(

            MDLabelA(
                text=message,
                adaptive_height=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1)
            ),

            y=y_position,
            duration=duration,
            pos_hint={ "right": 0.98, "top": 0.95 },
            size_hint_x=.55,
            md_bg_color=colors.get(
                msg_type,
                colors[Msg_type.info]
            ),

            padding=[dp(5),dp(5),dp(5),dp(5)]

        )
        close_btn = MDSnackbarActionButton(        
            text="CLOSE",        
            theme_text_color="Custom",        
            text_color=(1,1,1,1),        
            on_release=lambda x: self.remove_snackbar(snackbar)        
        )

        snackbar.add_widget(close_btn)
        self.active_snackbars.append(snackbar)
        snackbar.open()
        Clock.schedule_once( lambda dt: self.remove_snackbar(snackbar), duration + .3 )

        return snackbar

    def remove_snackbar(self, snackbar):

        if snackbar in self.active_snackbars:
            self.active_snackbars.remove(snackbar)

        snackbar.dismiss()

        self.rearrange()

    def rearrange(self):

        for index, snackbar in enumerate(
            self.active_snackbars
        ):

            snackbar.y = (
                dp(24)
                +
                dp(self.OFFSET_Y * index)
            )

    def close_all(self):

        for snackbar in self.active_snackbars:

            snackbar.dismiss()

        self.active_snackbars.clear()

snackbar_manager = SnackbarManager()