from kivy.lang import Builder
from kivy.properties import StringProperty , ObjectProperty
from kivymd.uix.card import MDCard
from cmn.resource_helper import PathManager

Builder.load_string(
    
"""
<MDCardA>:
    orientation: "vertical"
    size_hint_y: None
    height: dp(260)
    padding: dp(10)
    spacing: dp(5)
    elevation: 4
    radius: [dp(12)]

    MDBoxLayout:
        orientation: "vertical"
        size_hint_y: None
        height: dp(190)
        spacing: dp(8)

        # Row1 Title
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: dp(35)
            spacing: dp(10)

            MDLabelA:
                id: title_label
                text: root.title
                font_style: "H6"
                bold: True
                theme_text_color: "Primary"
                size_hint_x: 0.7
                size_hint_y: None
                height: dp(35)

        # Row2 Pronunciation
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: dp(25)

            MDLabelA:
                id: pronunciation_label
                text: root.pronunciation
                font_style: "Subtitle1"
                size_hint_x: 0.8
                halign: "left"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: dp(25)

        # Row3 Chips
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: dp(30)
            spacing: dp(3)

            MDChipA:
                id: pos_chip
                text: root.partOfSpeach
                icon: "alphabetical-variant"

            MDChipA:
                id: type_chip
                text: root.type_
                icon: "format-list-bulleted-type"

            MDChipA:
                id: level_chip
                text: root.level
                icon: "chart-bar"

            MDChipA:
                id: box_chip
                text: root.box
                icon: "package-variant"

        # Row4 Example
        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: dp(45)

            MDLabelA:
                text: "Example:"
                font_style: "Subtitle1"
                bold: True
                size_hint_y: None
                height: dp(20)

            MDLabelA:
                id: example_label
                text: root.example
                halign: "left"
                valign: "middle"

                text_size: self.width, None
                shorten: True
                shorten_from: "right"

                size_hint_y: None
                height: dp(20)

        # Row5 Collocation
        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: dp(45)

            MDLabelA:
                text: "Collocation:"
                font_style: "Subtitle1"
                bold: True
                size_hint_y: None
                height: dp(20)

            MDLabelA:
                id: collocation_label
                text: root.collocation
                halign: "left"
                valign: "middle"

                text_size: self.width, None
                shorten: True
                shorten_from: "right"

                size_hint_y: None
                height: dp(20)

        # Row6 Edit Button
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            padding: [0, dp(10), 0, 0]

            MDRaisedButton:
                text: "Edit Card"
                icon: "pencil"
                size_hint_x: 0.8
                pos_hint: {"center_x": 0.5}
                on_press: root.edit_card()
                md_bg_color: app.theme_cls.primary_color

"""

)

class MDCardA(MDCard):
    title = StringProperty()
    example = StringProperty()
    collocation = StringProperty()
    pronunciation = StringProperty()
    partOfSpeach = StringProperty()
    type_ = StringProperty()
    box = StringProperty()
    level = StringProperty()
    edit_card = ObjectProperty(None)
    pass  