from kivymd.uix.snackbar import MDSnackbar, MDSnackbarActionButton, MDSnackbarCloseButton
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp
from widgets.MDLabelA import MDLabelA


class SnackbarManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def show_snackbar(self, message, duration=3, msg_type="info", 
                     button_text=None, button_callback=None):
        
        colors = {
            "success": "#4CAF50",  # سبز
            "error": "#F44336",    # قرمز
            "warning": "#FF9800",  # نارنجی
            "info": "#000000"      # خاکستری
        }

        bg_color = colors.get(msg_type , colors["info"])
        
        snackbar = MDSnackbar(
            MDLabelA(
                text=message 
            ),
            y=dp(24),
            duration = duration,
            pos_hint={"right": 0.99 , "top": 0.95},
            size_hint_x=0.5,  
            md_bg_color=bg_color,
            padding=[dp(5), dp(5), dp(5), dp(5)],
        )

        if button_callback:
            snackbar.add_widget(MDSnackbarActionButton(
                text= button_text,
                theme_text_color="Custom",
                text_color="#FFFFFFFF",
                on_release = button_callback,
                padding=[dp(8), dp(8)],
                size_hint=(None, None),
                size=(dp(60), dp(32)), 
            ))

        snackbar.open()
        return snackbar

    def close_snackbar(self , snackbar):
        snackbar.dismiss()

snackbar_manager = SnackbarManager()