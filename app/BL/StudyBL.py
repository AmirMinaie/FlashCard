from app.DA.models import (
    bookDA,
    studyScheduleDA,
    studyScheduleItemDA,
    studySessionDA,
    constantDA
)

from app.DA.session import get_session
from datetime import datetime, date
from app.cmn.logger import logger


class StudyBL:

    def get_today_study(self):

        session = get_session()

        try:
            today = date.today()

            # -----------------------------------------
            # Get today's weekday
            # -----------------------------------------

            weekday_name = datetime.now().strftime("%A").lower()

            weekday = (
                session.query(constantDA)
                .filter(
                    constantDA.name == weekday_name,
                    constantDA.type == "Weekday"
                )
                .first()
            )

            if not weekday:
                return []

            # -----------------------------------------
            # Get active schedule
            # -----------------------------------------

            schedule = (
                session.query(studyScheduleDA)
                .filter(
                    studyScheduleDA.status.has(
                        name="active"
                    )
                )
                .first()
            )

            if not schedule:
                return []

            # -----------------------------------------
            # Get today's schedule items
            # -----------------------------------------

            items = (
                session.query(studyScheduleItemDA)
                .filter(
                    studyScheduleItemDA.schedule_id == schedule.id,
                    studyScheduleItemDA.weekday_id == weekday.id
                )
                .all()
            )

            result = []

            # -----------------------------------------
            # Calculate today's progress
            # -----------------------------------------

            for item in items:

                sessions = (
                    session.query(studySessionDA)
                    .filter(
                        studySessionDA.schedule_item_id == item.id,
                        studySessionDA.study_date == today
                    )
                    .all()
                )

                # Number of pages planned for today
                total_pages = item.pages

                # Number of pages actually completed
                completed_pages = sum(
                    study.completedPages or 0
                    for study in sessions
                )

                # Don't allow completed pages
                # to exceed planned pages
                completed_pages = min(
                    completed_pages,
                    total_pages
                )

                remaining_pages = max(
                    total_pages - completed_pages,
                    0
                )

                # -----------------------------------------
                # Status
                # -----------------------------------------

                if completed_pages == 0:

                    status = "pending"

                elif completed_pages >= total_pages:

                    status = "completed"

                else:

                    status = "in_progress"

                result.append({
                    "item": item,
                    "book": item.book,

                    "total_pages": total_pages,
                    "completed_pages": completed_pages,
                    "remaining_pages": remaining_pages,

                    "status": status,
                })

            return result

        except Exception as error:

            logger.exception(
                f"Error getting today's study: {error}"
            )

            return []

        finally:
            session.close()