from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
from cmn.resource_helper import resource_path

Builder.load_file(resource_path("app" , "widgets","MDCardA.kv"))

class MDCardA(MDCard):
    title = StringProperty()
    example = StringProperty()
    collocation = StringProperty()
    pronunciation = StringProperty()
    partOfSpeach = StringProperty()
    type_ = StringProperty()
    box = StringProperty()
    level = StringProperty()
    pass  