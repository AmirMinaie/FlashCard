from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.properties import ( NumericProperty, StringProperty, ObjectProperty, )
from kivy.clock import Clock
from kivy.metrics import dp
from app.widgets.StudyTaskCard import StudyTaskCard
from app.cmn.resource_helper import PathManager
from app.cmn.logger import logger
from app.cmn.utility import format_time
from app.BL.StudyBL import StudyBL
import time

Builder.load_file(str(PathManager.app_path("Kv/TodayStudyScreen.kv")))


class TodayStudyScreen(MDScreen):

    # ==================================================
    # Summary Properties
    # ==================================================

    total_tasks = NumericProperty(0)
    completed_tasks = NumericProperty(0)

    total_pages = NumericProperty(0)
    completed_pages = NumericProperty(0)
    remaining_pages = NumericProperty(0)

    # ==================================================
    # Current Session
    # ==================================================

    session_time = StringProperty("0s")

    current_task = ObjectProperty(None)

    # ==================================================
    # Initialization
    # ==================================================
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.study_bl = StudyBL()

        self.tasks = []

        # Timer
        self.session_timer = None
        self.session_start_time = None
        self.elapsed_time = 0

    # ==================================================
    # Lifecycle
    # ==================================================
    def on_kv_post(self, *args):
        self.reset_timer()
        self.load_today_study()

    # ==================================================
    # Load Today's Study
    # ==================================================
    def load_today_study(self):

        try:
            self.tasks = self.study_bl.get_today_study()
            self.update_summary()
            self.display_tasks()

        except Exception as error:
            logger.exception(f"Error loading today's study: {error}")

    # ==================================================
    # Summary
    # ==================================================
    def update_summary(self):

        self.total_tasks = len(self.tasks)

        self.completed_tasks = sum(
            1
            for task in self.tasks
            if task.get("status") == "completed"
        )

        self.total_pages = sum(
            task.get("total_pages", 0)
            for task in self.tasks
        )

        self.completed_pages = sum(
            task.get("completed_pages", 0)
            for task in self.tasks
        )

        self.remaining_pages = sum(
            task.get("remaining_pages", 0)
            for task in self.tasks
        )

    # ==================================================
    # Timer
    # ==================================================
    def start_timer(self):

        if self.session_timer:
            self.session_timer.cancel()

        self.session_start_time = time.perf_counter()

        self.session_timer = Clock.schedule_interval(
            self.update_session_time,
            1
        )

    def stop_timer(self):

        if self.session_timer:
            self.session_timer.cancel()
            self.session_timer = None

        if self.session_start_time is not None:
            elapsed = int(
                time.perf_counter()
                - self.session_start_time
            )

            self.elapsed_time += elapsed
            self.session_start_time = None

    def update_session_time(self, dt):

        if self.session_start_time is None:
            return

        current_elapsed = int(
            time.perf_counter()
            - self.session_start_time
        )

        total_elapsed = (
            self.elapsed_time
            + current_elapsed
        )

        self.session_time = format_time(
            total_elapsed
        )

    def reset_timer(self):

        if self.session_timer:
            self.session_timer.cancel()
            self.session_timer = None
        self.session_start_time = None
        self.elapsed_time = 0
        self.session_time = "0s"

    # ==================================================
    # Start / Continue Task
    # ==================================================
    def start_task(self, task):
    
        if not task:
            return
    
        if task.get("status") == "completed":
            return
    
        self.current_task = task
    
        self.reset_timer()
        self.start_timer()
    
        self.display_running_task()

    # ==================================================
    # Finish Task
    # ==================================================
    def finish_task(self, task=None):

        # Use passed task or current task
        if task is None:
            task = self.current_task

        if not task:
            return

        # Stop timer
        self.stop_timer()

        # Remaining pages become completed
        completed_pages = task.get(
            "remaining_pages",
            0
        )

        if completed_pages <= 0:

            self.current_task = None

            self.reset_timer()

            self.load_today_study()

            return

        # Save session

        try:

            success = self.study_bl.create_study_session(
                schedule_item_id=task["item"].id,
                completed_pages=completed_pages,
                study_date=None,
                duration_seconds=self.elapsed_time,
            )

            if success is False:
                logger.error(
                    "Failed to create study session."
                )
                return

            # 
            # Clear current task
            # 

            self.current_task = None

            self.reset_timer()

            # 
            # Reload from database
            # 

            self.load_today_study()

        except Exception as error:

            logger.exception(
                f"Error finishing study task: {error}"
            )

    # ==================================================
    # Save Partial Progress
    # ==================================================
    def save_progress(self, completed_pages):

        if not self.current_task:
            return

        task = self.current_task

        # Validate pages

        try:
            completed_pages = int(completed_pages)

        except (TypeError, ValueError):

            logger.warning(
                f"Invalid completed pages: {completed_pages}"
            )

            return

        if completed_pages <= 0:
            return

        # Don't exceed remaining pages


        completed_pages = min(
            completed_pages,
            task.get("remaining_pages", 0)
        )

        if completed_pages <= 0:
            return

        # Stop timer


        self.stop_timer()


        # Save session


        try:

            success = self.study_bl.create_study_session(
                schedule_item_id=task["item"].id,
                completed_pages=completed_pages,
                study_date=None,
                duration_seconds=self.elapsed_time,
            )

            if success is False:
                logger.error(
                    "Failed to save study progress."
                )
                return

            # 
            # Clear current task
            # 

            self.current_task = None

            self.reset_timer()

            # 
            # Reload data
            # 

            self.load_today_study()

        except Exception as error:

            logger.exception(
                f"Error saving study progress: {error}"
            )

    # ==================================================
    # Skip Task
    # ==================================================
    def skip_task(self, task=None):

        if task is None:
            task = self.current_task

        if not task:
            return


        # Stop current session


        self.stop_timer()


        # Clear current task


        self.current_task = None

        self.reset_timer()


        # Show task list again


        self.display_tasks()

    # ==================================================
    # Display Tasks
    # ==================================================
    def display_tasks(self):


        # Hide running area
        self.show_running_area(False)


        # Get container


        container = self.ids.tasks_container

        container.clear_widgets()


        # Create cards


        for task in self.tasks:

            widget = self.create_task_widget(task)

            if widget:

                container.add_widget(widget)

    # ==================================================
    # Create Task Card
    # ==================================================
    def create_task_widget(self, task):

        if not task:
            return None

        status = task.get("status", "pending")
        total_pages = task.get("total_pages",0)
        completed_pages = task.get("completed_pages",0)
        remaining_pages = task.get("remaining_pages",0)
        book = task.get("book")

        if not book:
            return None

        # ==================================================
        # Status
        # ==================================================

        if status == "pending":
            status_icon = ("book-open-page-variant-outline")
            status_color = (list(self.theme_cls.primary_color))

            button_text = "Start"
            button_icon = "play"
            task_text = "Ready to study"

        elif status == "in_progress":

            status_icon = "progress-clock"

            status_color = [1,0.55,0,1]

            button_text = "Continue"
            button_icon = "play"

            task_text = "Study in progress"

        elif status == "completed":

            status_icon = "check-circle"

            status_color = [0.3,0.7,0.3,1]

            button_text = "Done"
            button_icon = "check"

            task_text = "Completed"

        else:

            status_icon = (
                "book-open-page-variant-outline"
            )

            status_color = (
                list(self.theme_cls.primary_color)
            )

            button_text = "Start"
            button_icon = "play"

            task_text = "Ready to study"

        # ==================================================
        # Page Text
        # ==================================================

        if status == "completed":

            page_text = (
                f"{completed_pages} / "
                f"{total_pages} pages"
            )

        else:

            page_text = (
                f"{completed_pages} / "
                f"{total_pages} pages"
                f"  •  "
                f"{remaining_pages} remaining"
            )

        # ==================================================
        # Time
        # ==================================================

        time_text = ""

        # ==================================================
        # Create Widget
        # ==================================================

        widget = StudyTaskCard(

            item=task,
            book_title=book.title or "",
            task_text=task_text,
            page_text=page_text,
            time_text=time_text,
            button_text=button_text,
            button_icon=button_icon,
            status_icon=status_icon,
            status_color=status_color,
            on_start=self.start_task,
            on_finish=self.finish_task,
            on_skip=self.skip_task,
        )

        return widget

    # ==================================================
    # Running Task
    # ==================================================
    def display_running_task(self):

        if not self.current_task:
            return

        task = self.current_task

        book = task.get("book")

        if not book:
            return


        # Show running area


        self.show_running_area(True)


        # Book


        self.ids.running_book_label.text = (
            book.title or ""
        )


        # Task


        self.ids.running_task_label.text = (
            "Study in progress"
        )


        # Pages


        completed_pages = task.get(
            "completed_pages",
            0
        )

        total_pages = task.get(
            "total_pages",
            0
        )

        remaining_pages = task.get(
            "remaining_pages",
            0
        )

        self.ids.running_pages_label.text = (
            f"{completed_pages} / "
            f"{total_pages} pages"
        )

        self.ids.running_remaining_label.text = (
            f"{remaining_pages} pages remaining"
        )


        # Progress


        progress = 0

        if total_pages > 0:

            progress = (
                completed_pages
                / total_pages
                * 100
            )

        self.ids.running_progress.value = progress


        # Timer


        self.ids.running_timer_label.text = (
            self.session_time
        )

    # ==================================================
    # Show / Hide Running Area
    # ==================================================
    def show_running_area(self, visible):

        running_box = self.ids.running_study_box

        if visible:

            running_box.height = dp(230)
            running_box.opacity = 1
            running_box.disabled = False

        else:

            running_box.height = 0
            running_box.opacity = 0
            running_box.disabled = True

    # ==================================================
    # Refresh Running UI
    # ==================================================
    def update_running_progress(self):

        if not self.current_task:
            return

        task = self.current_task

        total_pages = task.get(
            "total_pages",
            0
        )

        completed_pages = task.get(
            "completed_pages",
            0
        )

        remaining_pages = task.get(
            "remaining_pages",
            0
        )

        if total_pages > 0:

            progress = (
                completed_pages
                / total_pages
                * 100
            )

        else:

            progress = 0

        self.ids.running_progress.value = progress

        self.ids.running_pages_label.text = (
            f"{completed_pages} / "
            f"{total_pages} pages"
        )

        self.ids.running_remaining_label.text = (
            f"{remaining_pages} pages remaining"
        )

    # ==================================================
    # Update Timer UI
    # ==================================================
    def update_running_timer(self):

        if not self.current_task:
            return

        if "running_timer_label" in self.ids:

            self.ids.running_timer_label.text = (
                self.session_time
            )

    # ==================================================
    # Go Back To Task List
    # ==================================================
    def cancel_current_task(self):

        if not self.current_task:
            return

        self.stop_timer()
        self.current_task = None
        self.reset_timer()
        self.display_tasks()