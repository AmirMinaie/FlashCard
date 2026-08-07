from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from cmn.resource_helper import *
from widgets.SnackbarManager import snackbar_manager , Msg_type
from widgets.MDLabelA import MDLabelA
from widgets.MDCardA import MDCardA
from widgets.MDChipA import MDChipA
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivy.properties import StringProperty, ListProperty, DictProperty, BooleanProperty, ObjectProperty 
from BL.FlashCardBL import FlashCardBL, OrderByConfig
from cmn.config_reader import ConfigReader
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.clock import Clock
from .AddFlashCardScreen import AddFlashCardScreen

Builder.load_file(str(PathManager.app_path("Kv/FlashCardListScreen.kv")))

class FlashCardListScreen(MDScreen):
    Filters = ConfigReader().get('filters_FlashCard_List')
    Curent_Filter_Id = ConfigReader().get('Defulte_filters_FlashCard_List')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_chips = {}
        self.search_text = ''
        self.exact_search = False
        self.flashcard_bl = FlashCardBL()
        self.current_page = 1
        self.page_size = ConfigReader().get("CardsPerPage")
        self.loading_more = False
        self.has_more = True
        self._scroll_trigger = None

    def on_kv_post(self, base_widget):
        self.create_filter_chips()
        self.load_flashcard(reset=True)
        self.update_filter_counts()
        # استفاده از Clock برای throttle کردن
        self.ids.RV.bind(scroll_y=self.schedule_check_scroll)

    def schedule_check_scroll(self, rv, value):
        """زمان‌بندی بررسی اسکرول با تاخیر"""
        if self._scroll_trigger:
            Clock.unschedule(self._scroll_trigger)
        self._scroll_trigger = Clock.schedule_once(
            lambda dt: self.check_scroll(rv, value), 0.1
        )

    def check_scroll(self, rv, value):
        """بررسی اسکرول برای لود بیشتر"""
        self.prev_scroll_value = value
        if value > 0.05 or value > self.prev_scroll_value:
            return
        
        snackbar_manager.show_snackbar(message=f"load page {len(self.ids.RV.data)} {value}", msg_type=Msg_type.info )
        if self.loading_more:
            return
        
        if not self.has_more:
            return
        
        self.loading_more = True
        
        self.current_page += 1
        self.load_flashcard(reset=False)

    def search_flashcards(self, search_text):
        """جستجو در فلش کارت‌ها"""
        self.search_text = search_text
        self.exact_search = self.ids.exact_switch.active
        Clock.unschedule(self._perform_search)
        Clock.schedule_once(lambda dt: self._perform_search(), 0.3)
    
    def _perform_search(self):
        """انجام جستجو با تاخیر"""
        self.load_flashcard(reset=True)
        self.update_filter_counts()

    def create_filter_chips(self):
        container = self.ids.filter_chips_container
        container.clear_widgets()
        self.filter_chips.clear()
        
        for filter_data in self.Filters:
            chip = FilterChip(
                filter_id=filter_data["id"],
                filter_icon=filter_data["icon"],
                text=filter_data["text"],
                base_text=filter_data["text"],
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
        self.load_flashcard(reset=True)
     
    def edit_card(self, card_id):
        """ویرایش کارت با آیدی مشخص"""
        app = MDApp.get_running_app()
        home_screen = app.root.get_screen("HomeScreen")

        for child in home_screen.walk(restrict=True):
            if child.__class__.__name__ == "MDBottomNavigation":
                for sub_child in child.children:
                    if hasattr(sub_child, 'get_screen'):
                        add_screen = sub_child.get_screen("add_tab")
                        if add_screen and add_screen.children:
                            add_flashcard = add_screen.children[0]
                            if hasattr(add_flashcard, 'set_card_id'):
                                add_flashcard.set_card_id(card_id)
                                child.switch_tab("add_tab")
                        break
                break

    def load_flashcard(self, reset=False):
        """لود فلش کارت‌ها"""
        if reset:
            self.ids.RV.data = []
            self.current_page = 1
            self.has_more = True

        Curent_Filter = next(
            (item for item in self.Filters if item.get("id") == self.Curent_Filter_Id), 
            None
        )

        flashcardList = self.flashcard_bl.get_cards(
            order=Curent_Filter.get('order') if Curent_Filter else None,
            SearchText=self.search_text or '',
            exact_search=self.exact_search,
            where=Curent_Filter.get('where') if Curent_Filter else None,
            page=self.current_page,
            page_size=self.page_size
        )

        def make_edit_func(card_id):
            return lambda: self.edit_card(card_id)

        if len(flashcardList) < self.page_size:
            self.has_more = False
        
        new_data = [
            {       
                'title': flashcard.title or "",
                'example': flashcard.example or "",
                'collocation': flashcard.collocation or "",
                'pronunciation': flashcard.pronunciation or "",
                'partOfSpeach': getattr(flashcard.pos, 'caption', 'N/A'),
                'type_': getattr(flashcard.type_, 'caption', 'N/A'),
                'box': getattr(flashcard.box, 'caption', 'N/A'),
                'level': getattr(flashcard.level, 'caption', 'N/A'),
                'last_review_quality': str(flashcard.last_review_quality or ""),
                'last_review_date': (
                    flashcard.last_review_date.strftime("%Y-%m-%d")
                    if flashcard.last_review_date
                    else ""
                ),
                'edit_card': make_edit_func(flashcard.id)
            }
            for flashcard in flashcardList
        ]

        if reset:
            self.ids.RV.data = new_data
        else:
            if new_data:
                self.ids.RV.data.extend(new_data)
        
        Clock.schedule_once(lambda dt: self.reset_loading_flag(), 0.5)

    def reset_loading_flag(self):
        """ریست فلگ لودینگ با تاخیر"""
        self.loading_more = False

    def update_filter_counts(self):
        """به‌روزرسانی تعداد فیلترها"""
        for filter_data in self.Filters:
            count = self.flashcard_bl.get_cards_count(
                SearchText=self.search_text,
                exact_search=self.exact_search,
                where=filter_data.get("where")
            )

            chip = self.filter_chips.get(filter_data["id"])

            if chip:
                chip.text = f"{chip.base_text} {count}"

class FilterChip(MDChipA, RoundedRectangularElevationBehavior):
    """چیپ سفارشی برای فیلترها"""
    filter_type = StringProperty()
    base_text = StringProperty("")
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