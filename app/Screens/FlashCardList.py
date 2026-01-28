from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList, MDListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from BL.FlashCardBL import FlashCardBL
from kivy.lang import Builder
from cmn.resource_helper import *

Builder.load_file(resource_path("app","Kv/FlashCardList.kv"))

class FlashCardList(MDScreen):
    def on_pre_enter(self):
        Clock.schedule_once(self.load_cards)

    def load_cards(self, dt):
        container = self.ids.container
        container.clear_widgets()

        bl = FlashCardBL()
        cards = bl.get_today_flashcards()

        if not cards:
            container.add_widget(MDLabel(text="No flashcards for today", halign="center"))
            return

        for card in cards:
            md_card = MDCard(
                orientation="vertical",
                padding=10,
                size_hint=(1, None),
                height=120,
                radius=[15,],
                elevation=6,
                ripple_behavior=True  # افکت لمس
            )
            md_card.add_widget(
                ThreeLineListItem(
                    text=f"Q: {card.question}",
                    secondary_text=f"A: {card.answer}",
                    tertiary_text=f"Created: {card.created_at.strftime('%H:%M %d/%m/%Y')}",
                )
            )
            container.add_widget(md_card)
