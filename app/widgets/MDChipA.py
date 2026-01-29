from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
from kivymd.uix.chip import MDChip, MDChipLeadingIcon, MDChipText
from widgets.MDLabelA import MDLabelA
from kivymd.uix.label import MDLabel
from cmn.resource_helper import resource_path

class MDChipA(MDChip):
    chip_text = StringProperty("title")
    icon  = StringProperty("message")
    pass

Builder.load_string('''
MDChip:
    size_hint: None, None
    size: dp(70), dp(32)

    MDChipLeadingIcon:
        icon: "message"

    MDLabelA:
        text: "11"

''')