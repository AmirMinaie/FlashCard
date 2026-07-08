from kivy.properties import StringProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.clock import Clock
from threading import Thread
from widgets.BaseButtonA import BaseButtonA
from kivy.utils import get_color_from_hex
from cmn.logger import logger
from kivymd.uix.dialog import MDDialog

Builder.load_string('''
<AsyncButton>:
    size_hint: None, None
    size: dp(120), dp(48)
''')

class AsyncButton(BaseButtonA):
    before = ObjectProperty(None, allownone=True)
    task = ObjectProperty(None, allownone=True)
    after = ObjectProperty(None, allownone=True)
    error_handler = ObjectProperty(None, allownone=True)
    loading = BooleanProperty(False)
    confirm = BooleanProperty(False)
    confirm_title = StringProperty("")
    confirm_text = StringProperty("")


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_press=self._on_press)

    def _on_press(self, *args):
        if self.loading:
            return

        if self.confirm:
            if getattr(self, "dialog", None):
                return
            self._show_confirm_dialog()
            return

        self._start_task()
    
    def _start_task(self):
        try:
            if self.before and not self.before():
                return
        except Exception as e:
            logger.error(str(e))

            if callable(self.error_handler):
                self.error_handler(e)

            return

        self.loading = True
        self.disabled = True

        Thread(target=self._run_task, daemon=True).start()

    def _show_confirm_dialog(self):
        self.dialog = MDDialog(
            title=self.confirm_title,
            text=self.confirm_text,
            buttons=[
                BaseButtonA(
                    text="CANCEL",
                    on_release=lambda x: self._cancel_confirm()
                ),
                BaseButtonA(
                    text="OK",
                    on_release=self._confirm
                )
            ]
        )

        self.dialog.open()

    def _cancel_confirm(self):
        self.dialog.dismiss()
        self.dialog = None

    def _confirm(self, *args):
        self.dialog.dismiss()
        self.dialog = None
        self._start_task()

    def _run_task(self):

        try:
            result = self.task() if callable(self.task) else None
            Clock.schedule_once(lambda dt: self._finish(result))

        except Exception as e:
            Clock.schedule_once(lambda dt, err=e: self._error(err))

    def _finish(self, result):
        self.loading = False
        self.disabled = False

        if callable(self.after):
            self.after(result)

    def _error(self, e):
        self.loading = False
        self.disabled = False

        if callable(self.error_handler ):
            self.error_handler(e)