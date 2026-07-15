from kivy.lang import Builder
from kivy.metrics import dp

from widgets.AsyncBehavior import AsyncBehavior
from widgets.BaseButtonA import BaseButtonA

Builder.load_string("""
<AsyncButton>:
    size_hint: None, None
    size: dp(120), dp(48)
""")


class AsyncButton(AsyncBehavior, BaseButtonA):
    pass