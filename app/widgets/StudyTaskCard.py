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
    adaptive_height: True

    padding: dp(16)
    spacing: dp(8)

    radius: [20]
    elevation: 2

    # ==================================================
    # Header
    # ==================================================

    MDBoxLayout:
        adaptive_height: True
        spacing: dp(10)

        MDIcon:
            icon: root.status_icon

            theme_icon_color: "Custom"
            icon_color: root.status_color

            size_hint_x: None
            width: dp(32)

        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            spacing: dp(2)

            MDLabelA:
                text: root.book_title
                font_style: "H6"
                bold: True

                max_lines: 1
                shorten: True
                shorten_from: "right"

            MDLabelA:
                text: root.task_text
                theme_text_color: "Secondary"

                max_lines: 1
                shorten: True
                shorten_from: "right"


    # ==================================================
    # Page / Time
    # ==================================================

    MDSeparator:


    MDBoxLayout:
        adaptive_height: True
        spacing: dp(8)

        MDLabelA:
            text: root.page_text

            max_lines: 1
            shorten: True
            shorten_from: "right"

        MDLabelA:
            text: root.time_text

            halign: "right"
            theme_text_color: "Secondary"

            max_lines: 1
            shorten: True
            shorten_from: "left"


    # ==================================================
    # Action
    # ==================================================

    MDBoxLayout:
        adaptive_height: True
        spacing: dp(8)

        Widget:


        BaseButtonA:
            text: root.button_text
            icon: root.button_icon

            size_hint_x: None
            width: dp(120)

            on_release: root.handle_action()
""")


class StudyTaskCard(MDCard):

    # ==================================================
    # Data
    # ==================================================

    # Complete task dictionary returned by StudyBL
    #
    # {
    #     "item": studyScheduleItemDA,
    #     "book": bookDA,
    #     "total_pages": 10,
    #     "completed_pages": 4,
    #     "remaining_pages": 6,
    #     "status": "in_progress"
    # }
    item = ObjectProperty(None)


    # ==================================================
    # Display
    # ==================================================

    book_title = StringProperty("")
    task_text = StringProperty("")
    page_text = StringProperty("")
    time_text = StringProperty("")


    # ==================================================
    # Action Button
    # ==================================================

    button_text = StringProperty("")
    button_icon = StringProperty("")


    # ==================================================
    # Status
    # ==================================================

    status_icon = StringProperty("")

    # Kivy colors are RGBA lists:
    #
    # [1, 1, 1, 1]
    # [0, 1, 0, 1]
    #
    status_color = ListProperty([1, 1, 1, 1])


    # ==================================================
    # Callbacks
    # ==================================================

    on_start = ObjectProperty(None)
    on_finish = ObjectProperty(None)
    on_skip = ObjectProperty(None)


    # ==================================================
    # Action Handler
    # ==================================================

    def handle_action(self):

        # ----------------------------------------------
        # Start / Continue
        # ----------------------------------------------

        if self.button_text in ("Start", "Continue"):

            if self.on_start:
                self.on_start(self.item)

            return


        # ----------------------------------------------
        # Finish
        # ----------------------------------------------

        if self.button_text == "Finish":

            if self.on_finish:
                self.on_finish(self.item)

            return


        # ----------------------------------------------
        # Skip
        # ----------------------------------------------

        if self.button_text == "Skip":

            if self.on_skip:
                self.on_skip(self.item)

            return