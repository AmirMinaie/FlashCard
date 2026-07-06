from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from BL.DashboardBL import DashboardBL
from cmn.logger import logger
from cmn.resource_helper import *
from kivymd.app import MDApp
from kivy.clock import Clock


Builder.load_file(str(PathManager.app_path("Kv/DashboardScreen.kv")))


class DashboardScreen(MDScreen):

    def on_kv_post(self, *args):
        Clock.schedule_once(lambda dt: self.ids.refresh_btn._on_press(), 0)


    def load_dashboard_data(self):
        dashboardBl = DashboardBL()
    
        return {
            "summary": dashboardBl.get_summary(),
            "learning_progress": dashboardBl.get_learning_progress(),
            "upcoming_reviews": dashboardBl.get_upcoming_reviews(),
            "estimated_study_time": dashboardBl.get_estimated_study_time(),
            "today_performance": dashboardBl.get_today_performance(),
        }

    def befor_load_dashboard(self):
        return True
    
    def after_load_dashboard(self, data):

        self.summary = data["summary"]
        self.learning_progress = data["learning_progress"]
        self.upcoming_reviews = data["upcoming_reviews"]
        self.estimated_study_time = data["estimated_study_time"]
        self.today_performance = data["today_performance"]

        ####################################################
        # TODAY
        ####################################################

        self.ids.today_review_label.text = f"{self.summary.today_reviews} Reviews Completed"
        self.ids.remaining_label.text = f"{self.summary.remaining_reviews} cards remaining"
        self.ids.completion_percent.text = f"{self.summary.today_progress:.2f}%"
        self.ids.today_progress.value = self.summary.today_progress

        ####################################################
        # SUMMARY
        ####################################################

        self.ids.streak_label.text = f"{self.summary.streak} Days"
        self.ids.due_today_label.text = str(self.summary.due_today)
        self.ids.total_cards_label.text = f"{self.learning_progress.total_cards:,}"
        self.ids.mature_label.text = str(self.learning_progress.mature_cards)

        quality = self.today_performance.average_quality

        self.ids.Today_Performance_label.text = (
            f"{quality:.2f}  {self.today_performance.success_rate}%"
        )

        stars = [
            self.ids.star1,
            self.ids.star2,
            self.ids.star3,
            self.ids.star4,
            self.ids.star5,
        ]

        full = int(quality)
        half = (quality - full) >= 0.5

        for i, star in enumerate(stars):
            if i < full:
                star.icon = "star"
            elif i == full and half:
                star.icon = "star-half-full"
            else:
                star.icon = "star-outline"

        ####################################################
        # LEARNING PROGRESS
        ####################################################

        self.ids.new_count.text = (
            f"{self.learning_progress.new_cards} ({self.learning_progress.new_percent:.2f}%)"
        )

        self.ids.learning_count.text = (
            f"{self.learning_progress.learning_cards} ({self.learning_progress.learning_percent:.2f}%)"
        )

        self.ids.review_count.text = (
            f"{self.learning_progress.review_cards} ({self.learning_progress.review_percent:.2f}%)"
        )

        self.ids.mature_count.text = (
            f"{self.learning_progress.mature_cards} ({self.learning_progress.mature_percent:.2f}%)"
        )

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

        self.ids.study_time_label.text = self.format_estimated_study_time(
            self.estimated_study_time
        )

    def handle_load_dashboard(self, e):
        logger.error(str(e))
        MDApp.get_running_app().show_message(
            str(e),
            msg_type="error"
        )
    
    def format_estimated_study_time(self ,  seconds):

        if seconds < 60:
            return f"{seconds} s"

        minutes = seconds // 60

        if minutes < 60:
            return f"{minutes} m"

        hours = minutes // 60
        minutes %= 60

        return f"{hours}h {minutes} m"