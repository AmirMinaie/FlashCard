from kivymd.uix.card import MDCard
from kivy.lang import Builder
from kivy.properties import (
    StringProperty,
    ObjectProperty,
    ListProperty,
)


Builder.load_string("""
<StudyTaskCard>:

    orientation: "vertical"

    size_hint_y: None
    height: dp(166)

    padding: dp(12)
    spacing: dp(6)

    radius: [16]
    elevation: 2


    # ==================================================
    # Header
    # ==================================================

    MDBoxLayout:
        orientation: "horizontal"

        size_hint_y: None
        height: dp(42)

        spacing: dp(10)


        # ----------------------------------------------
        # Status Icon
        # ----------------------------------------------

        MDBoxLayout:
            size_hint_x: None
            width: dp(32)

            MDIcon:
                icon: root.status_icon

                theme_icon_color: "Custom"
                icon_color: root.status_color

                size_hint: None, None
                size: dp(28), dp(28)

                pos_hint:
                    {"center_x": .5, "center_y": .5}


        # ----------------------------------------------
        # Book Information
        # ----------------------------------------------

        MDBoxLayout:
            orientation: "vertical"

            size_hint_x: 1
            size_hint_y: None
            height: dp(40)

            spacing: 0

            pos_hint:
                {"center_y": .5}


            MDLabelA:
                text: root.book_title

                font_style: "H6"
                bold: True

                size_hint_y: None
                height: dp(35)

                valign: "middle"

                max_lines: 1
                shorten: True
                shorten_from: "right"


            MDLabelA:
                text: root.task_text

                theme_text_color: "Secondary"

                size_hint_y: None
                height: dp(19)

                valign: "middle"

                max_lines: 1
                shorten: True
                shorten_from: "right"


    # ==================================================
    # Separator
    # ==================================================
    MDSeparator:

    # ==================================================
    # Page Information
    # ==================================================

    MDBoxLayout:
        orientation: "horizontal"

        size_hint_y: None
        height: dp(28)

        spacing: dp(8)


        MDLabelA:
            text: root.page_text

            size_hint_x: 1

            valign: "middle"
            halign: "left"

            max_lines: 1
            shorten: True
            shorten_from: "right"


        MDLabelA:
            text: root.time_text

            size_hint_x: None
            width: dp(55)

            valign: "middle"
            halign: "right"

            theme_text_color: "Secondary"

            max_lines: 1
            shorten: True
            shorten_from: "left"

    # ==================================================
    # Action
    # ==================================================

    MDBoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: dp(36) 
        spacing: dp(8)

        Widget:

        BaseButtonA:
            text: root.button_text
            icon: root.button_icon

            size_hint: None, None
            size: dp(106), dp(36)

            on_release: root.handle_action()
""")


class StudyTaskCard(MDCard):

    # ==================================================
    # Task
    # ==================================================

    item = ObjectProperty(None)

    # ==================================================
    # Text
    # ==================================================

    book_title = StringProperty("")
    task_text = StringProperty("")
    page_text = StringProperty("")
    time_text = StringProperty("")

    # ==================================================
    # Button
    # ==================================================

    button_text = StringProperty("")
    button_icon = StringProperty("")

    # ==================================================
    # Status
    # ==================================================

    status_icon = StringProperty("")
    status_color = ListProperty([1, 1, 1, 1])

    # ==================================================
    # Callbacks
    # ==================================================
    def __init__(self, **kwargs):

        self.on_start = None
        self.on_finish = None
        self.on_skip = None

        super().__init__(**kwargs)

    # ==================================================
    # Action
    # ==================================================
    def handle_action(self):

        if self.button_text in ("Start", "Continue"):

            if self.on_start:
                self.on_start(self.item)

            return

        if self.button_text == "Finish":

            if self.on_finish:
                self.on_finish(self.item)

            return

        if self.button_text == "Skip":

            if self.on_skip:
                self.on_skip(self.item)

            return