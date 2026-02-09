from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty
from kivymd.uix.chip import MDChip

Builder.load_string('''
<MDChipA>
    text: ""
    icon: ""
    type: "assist"
    theme_bg_color: "Custom"
    md_bg_color: "#d4d0d02e"
    theme_line_color: "Custom"
    line_color: "grey"
    theme_elevation_level: "Custom"
    elevation_level: 1
    theme_shadow_softness: "Custom"
    shadow_softness: 2
    line_width: dp(0.1)
                        

    MDChipLeadingIcon:
        icon: root.icon
        theme_text_color: "Custom"
        text_color: "#0697f7"

    MDChipText:
        text: root.text
        theme_text_color: "Custom"
        text_color: "#000000"
''')

class MDChipA(MDChip):
    pass