from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout

Builder.load_string('''
<SongItem>:
    orientation: "horizontal"
    adaptive_height: True

    padding: "12dp", "6dp"
    spacing: "8dp"

    canvas.before:
        Color:
            rgba: app.theme_cls.bg_normal
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8]

    MDBoxLayout:
        adaptive_height: True
        size_hint_x: 1
        valign: "middle"
    
        MDLabelA:
            text: root.text
            adaptive_height: True
            text_size: self.width, None
            halign: "left"
            valign: "middle"

    MDIconButton:
        icon: "delete"
        size_hint: None, None
        size: "36dp", "36dp"
        opacity: 1 if root.allow_delete else 0
        disabled: not root.allow_delete
        on_release: root.on_delete()

''')


class SongItem(MDBoxLayout):

    text = StringProperty("")
    allow_delete = BooleanProperty(False)

    song = ObjectProperty(allownone=True)

    select_callback = ObjectProperty(None)
    delete_callback = ObjectProperty(None)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self.select_callback:
                self.select_callback(self.song)
        return super().on_touch_up(touch)

    def on_delete(self):
        if self.delete_callback:
            self.delete_callback(self.song)