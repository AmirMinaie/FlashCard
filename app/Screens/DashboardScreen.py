from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from BL.DashboardBL import DashboardBL

from cmn.resource_helper import *

Builder.load_file(str(PathManager.app_path("Kv/DashboardScreen.kv")))


class DashboardScreen(MDScreen):

    def on_kv_post(self, *args):
        self.load_dashboard()

    def load_data(self):
        dashboardBl = DashboardBL()
        self.summary = dashboardBl.get_summary()
        self.learning_progress = dashboardBl.get_learning_progress()
        self.upcoming_reviews = dashboardBl.get_upcoming_reviews()
        self.estimated_study_time = dashboardBl.get_estimated_study_time()

    def load_dashboard(self):
        self.load_data()
        ####################################################
        # TODAY
        ####################################################
        
        self.ids.today_review_label.text = (f"{self.summary.today_reviews} Reviews Completed")
        self.ids.remaining_label.text = (f"{self.summary.remaining_reviews} cards remaining")
        self.ids.completion_percent.text = (f"{self.summary.today_progress:.2f}%")
        self.ids.today_progress.value = self.summary.today_progress

        ####################################################
        # SUMMARY
        ####################################################
        self.ids.streak_label.text = (f"{self.summary.streak} Days")
        self.ids.due_today_label.text = str(self.summary.due_today)
        self.ids.total_cards_label.text = (f"{self.learning_progress.total_cards:,}")
        self.ids.mature_label.text = str(self.learning_progress.mature_cards)

        ####################################################
        # LEARNING PROGRESS
        ####################################################

        self.ids.new_count.text = (f"{self.learning_progress.new_cards} ({self.learning_progress.new_percent:.2f}%)")
        self.ids.learning_count.text = (f"{self.learning_progress.learning_cards} ({self.learning_progress.learning_percent:.2f}%)")
        self.ids.review_count.text = (f"{self.learning_progress.review_cards} ({self.learning_progress.review_percent:.2f}%)")
        self.ids.mature_count.text = (f"{self.learning_progress.mature_cards} ({self.learning_progress.mature_percent:.2f}%)")

        self.ids.new_progress.value = self.learning_progress.new_percent
        self.ids.learning_progress.value = self.learning_progress.learning_percent
        self.ids.review_progress.value = self.learning_progress.review_percent
        self.ids.mature_progress.value = self.learning_progress.mature_percent

        ####################################################
        # UPCOMING
        ####################################################

        self.ids.tomorrow_label.text = str(self.upcoming_reviews.tomorrow)
        self.ids.next3_label.text = str(self.upcoming_reviews.next3)
        self.ids.next7_label.text = str(self.upcoming_reviews.next7)
        self.ids.next30_label.text = str(self.upcoming_reviews.next30)

        self.ids.study_time_label.text =self.format_estimated_study_time( self.estimated_study_time)

    def format_estimated_study_time(self ,  seconds):

        if seconds < 60:
            return f"{seconds} s"

        minutes = seconds // 60

        if minutes < 60:
            return f"{minutes} m"

        hours = minutes // 60
        minutes %= 60

        return f"{hours}h {minutes} m"
