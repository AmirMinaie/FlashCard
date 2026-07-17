from threading import Thread

from kivy.clock import Clock
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty

from cmn.logger import logger
from kivymd.uix.dialog import MDDialog
from widgets.BaseButtonA import BaseButtonA


class AsyncBehavior:
    before = ObjectProperty(None, allownone=True)
    task = ObjectProperty(None, allownone=True)
    after = ObjectProperty(None, allownone=True)
    error_handler = ObjectProperty(None, allownone=True)

    loading = BooleanProperty(False)

    confirm = BooleanProperty(False)
    confirm_title = StringProperty("")
    confirm_text = StringProperty("")

    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_press=self._on_press)

    def _on_press(self, *args):
        if self.loading:
            return

        if self.confirm:
            if self.dialog:
                return

            self._show_confirm_dialog()
            return

        self._start_task()

    def _start_task(self):
        self.loading = True
        self.disabled = True

        try:
            if self.before and not self.before():
                self.loading = False
                self.disabled = False 
                return

        except Exception as e:
            logger.error(str(e))

            if callable(self.error_handler):
                self.error_handler(e)

            return

        Thread( target=self._run_task, daemon=True ).start()

    def _show_confirm_dialog(self):
        self.dialog = MDDialog(
            title=self.confirm_title,
            text=self.confirm_text,
            buttons=[
                BaseButtonA(
                    text="CANCEL",
                    on_release=lambda x: self._cancel_confirm(),
                ),
                BaseButtonA(
                    text="OK",
                    on_release=self._confirm,
                ),
            ],
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

            Clock.schedule_once( lambda dt: self._finish(result) )

        except Exception as e:
            Clock.schedule_once( lambda dt, err=e: self._error(err) )

    def _finish(self, result):
        if callable(self.after):
            self.after(result)
        
        self.loading = False
        self.disabled = False 

    def _error(self, e):
        self.loading = False
        self.disabled = False

        if callable(self.error_handler):
            self.error_handler(e)