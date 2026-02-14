from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from cmn.resource_helper import *
from widgets.MDLabelA import MDLabelA
from widgets.MDCardA import MDCardA
from widgets.MDChipA import MDChipA
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivy.properties import StringProperty, ListProperty, DictProperty, BooleanProperty , ObjectProperty 
from BL.FlashCardBL import FlashCardBL , OrderByConfig
from cmn.config_reader import ConfigReader
from kivy.metrics import dp
from kivymd.app import MDApp
from .AddFlashCardScreen import AddFlashCardScreen

Builder.load_file(resource_path("app/Kv/FlashCardListScreen.kv"))

class FlashCardListScreen(MDScreen):
    Filters = ConfigReader().get('filters_FlashCard_List')
    Curent_Filter_Id = ConfigReader().get('Defulte_filters_FlashCard_List')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_chips = {}
        self.search_text = ''

    def on_kv_post(self, base_widget):
        self.create_filter_chips()
        self.load_flashcard()

    def search_flashcards(self, search_text):
        """جستجو در فلش کارت‌ها"""
        from kivy.clock import Clock
        self.search_text = search_text
        Clock.unschedule(self._perform_search)
        Clock.schedule_once(lambda dt: self._perform_search(search_text), 0.3)
    
    def _perform_search(self, search_text):
        """انجام جستجو با تاخیر"""
        self.load_flashcard()

    def create_filter_chips(self):
        container = self.ids.filter_chips_container
        container.clear_widgets()
        self.filter_chips.clear()
        
        for filter_data in self.Filters:
            chip = FilterChip(
                filter_id=filter_data["id"],
                filter_icon=filter_data["icon"],
                text=filter_data["text"],
                filter_type=filter_data["color"],
                size_hint=(None, None),
                size=(dp(140), dp(32)),
                radius=[dp(16),],
                on_chip_selected=self.on_filter_selected
            )
            
            if filter_data["id"] == self.Curent_Filter_Id:
                chip.select()
            
            container.add_widget(chip)
            self.filter_chips[filter_data["id"]] = chip

    def on_filter_selected(self, selected_chip):
        """وقتی فیلتری انتخاب می‌شود"""
        for chip_id, chip in self.filter_chips.items():
            if chip != selected_chip:
                chip.deselect()
        
        selected_chip.select()
        self.Curent_Filter_Id = selected_chip.filter_id
        self.load_flashcard()
     
    def edit_card(self , card_id):
        current = self
        while current.__class__.__name__ != "HomeScreen":
            current = current.parent
        home_screen = current
        
        bottom_nav = None
        for child in home_screen.children:
            if child.__class__.__name__ == "MDBottomNavigation":
                bottom_nav = child
                break
        
        if not bottom_nav:
            return
        
        screen_manager = None
        for child in bottom_nav.children:
            if child.__class__.__name__ == "ScreenManager":
                screen_manager = child
                break
        
        if not screen_manager:
            return
        
        add_screen =  screen_manager.get_screen("add_tab")
        
        if add_screen:

            add_screen.mode = "edit"
            add_screen.card_id = card_id
            bottom_nav.switch_tab("add_tab")  # یا 2 بسته به ترتیب

        print(f"edit Card {card_id}")
        pass

    def load_flashcard(self):
        Curent_Filter = next((item for item in self.Filters if item.get("id") == self.Curent_Filter_Id), None)
        flashcardList = FlashCardBL().get_cards(
            order=Curent_Filter.get('order'),
            SearchText=self.search_text or '',
            where=Curent_Filter.get('where')
            )
        def make_edit_func(card_id):
            return lambda: self.edit_card(card_id)
        
        self.ids.RV.data = [
        {       
            'title': flashcard.title or "",
            'example': flashcard.example or "",
            'collocation': flashcard.collocation or "",
            'pronunciation': flashcard.pronunciation or "",
            'partOfSpeach': getattr(flashcard.pos, 'caption', 'N/A'),
            'type_': getattr(flashcard.type_, 'caption', 'N/A'),
            'box': getattr(flashcard.box, 'caption', 'N/A'),
            'level': getattr(flashcard.level, 'caption', 'N/A'),
            'edit_card': make_edit_func(flashcard.id)
        }
        for flashcard in flashcardList
    ]

class FilterChip(MDChipA, RoundedRectangularElevationBehavior):
    """چیپ سفارشی برای فیلترها"""
    filter_type = StringProperty()
    filter_id = StringProperty()
    is_selected = BooleanProperty(False)
    filter_icon = StringProperty()

    def __init__(self, on_chip_selected=None, **kwargs):
        super().__init__(**kwargs)
        self._on_chip_selected = on_chip_selected
        self.bind(on_release=self.on_chip_press)
    
    def on_chip_press(self, instance):
        """وقتی چیپ فشرده می‌شود"""
        if self._on_chip_selected:
            self._on_chip_selected(self)
    
    def select(self):
        """انتخاب چیپ"""
        self.is_selected = True
        self.md_bg_color = self.theme_cls.primary_color
        self.text_color = [1, 1, 1, 1]  # سفید
        self.line_color = self.theme_cls.primary_color
        self.line_width = dp(1.5)
        
    def deselect(self):
        """لغو انتخاب چیپ"""
        self.is_selected = False
        self.md_bg_color = self.theme_cls.bg_dark
        self.text_color = self.theme_cls.text_color
        self.line_color = [0, 0, 0, 0]
        self.line_width = dp(0.1)