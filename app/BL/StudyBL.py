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

            # ------------------------------------------
            # Active schedule
            # ------------------------------------------

            schedule = (
                session.query(studyScheduleDA)
                .filter(
                    studyScheduleDA.status.has(name="active")
                )
                .first()
            )

            if not schedule:
                return []

            # ------------------------------------------
            # Today's schedule items
            # ------------------------------------------

            items = (
                session.query(studyScheduleItemDA)
                .filter(
                    studyScheduleItemDA.schedule_id == schedule.id,
                    studyScheduleItemDA.weekday_id == weekday.id
                )
                .all()
            )

            result = []

            for item in items:

                total_pages = item.pages or 0
                book = item.book

                # ------------------------------------------
                # Today's sessions
                # ------------------------------------------

                sessions = (
                    session.query(studySessionDA)
                    .filter(
                        studySessionDA.schedule_item_id == item.id,
                        studySessionDA.study_date == today
                    )
                    .order_by(
                        studySessionDA.start_page.asc()
                    )
                    .all()
                )

                # ------------------------------------------
                # Determine today's starting page
                # ------------------------------------------

                if sessions:

                    # The first page planned for today
                    start_page = sessions[0].start_page

                    # Last page actually completed today
                    last_completed_page = max(
                        study.end_page
                        for study in sessions
                    )

                    next_page = last_completed_page + 1

                else:

                    # No session today yet.
                    # current_page means last page read.
                    start_page = book.current_page

                    next_page = start_page

                # ------------------------------------------
                # Planned end page
                # ------------------------------------------

                end_page = (
                    start_page + total_pages - 1
                    if total_pages > 0
                    else start_page
                )

                # ------------------------------------------
                # Calculate completed pages
                # ------------------------------------------

                completed_pages = 0

                if sessions:

                    # Count unique pages instead of simply
                    # summing session lengths.
                    studied_pages = set()

                    for study in sessions:

                        for page in range(
                            study.start_page,
                            study.end_page + 1
                        ):
                            studied_pages.add(page)

                    completed_pages = len(studied_pages)

                completed_pages = min(
                    completed_pages,
                    total_pages
                )

                # ------------------------------------------
                # Remaining pages
                # ------------------------------------------

                remaining_pages = max(
                    total_pages - completed_pages,
                    0
                )

                # ------------------------------------------
                # Completed range
                # ------------------------------------------

                if completed_pages > 0:

                    completed_start_page = start_page

                    completed_end_page = (
                        start_page + completed_pages - 1
                    )

                else:

                    completed_start_page = None
                    completed_end_page = None

                # ------------------------------------------
                # Remaining range
                # ------------------------------------------

                if remaining_pages > 0:

                    remaining_start_page = (
                        start_page + completed_pages
                    )

                    remaining_end_page = end_page

                else:

                    remaining_start_page = None
                    remaining_end_page = None

                # ------------------------------------------
                # Status
                # ------------------------------------------

                if completed_pages == 0:

                    status = "pending"

                elif completed_pages >= total_pages:

                    status = "completed"

                else:

                    status = "in_progress"

                # ------------------------------------------
                # Result
                # ------------------------------------------

                result.append({

                    "item": item,
                    "book": book,

                    # Planned
                    "total_pages": total_pages,

                    # Progress
                    "completed_pages": completed_pages,
                    "remaining_pages": remaining_pages,

                    # Full planned range
                    "start_page": start_page,
                    "end_page": end_page,

                    # Current / next
                    "next_page": next_page,

                    # Completed range
                    "completed_start_page": completed_start_page,
                    "completed_end_page": completed_end_page,

                    # Remaining range
                    "remaining_start_page": remaining_start_page,
                    "remaining_end_page": remaining_end_page,

                    # Status
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

    def create_study_session( self, schedule_item_id, start_page , end_page, study_date=None, duration_seconds=0, ):

        session = get_session()

        try:

            if not schedule_item_id:
                logger.warning("schedule_item_id is required.")
                return False

            try:
                start_page = int(start_page or 0)
                end_page = int(end_page or 0)
                duration_seconds = int(duration_seconds or 0)

            except (TypeError, ValueError):
                logger.warning("Invalid study session values.")
                return False

            if end_page < start_page:
                logger.warning(f"Invalid page range: {start_page} -> {end_page}")
                return False

            if duration_seconds < 0:
                duration_seconds = 0

            # ------------------------------------------
            # Check schedule item
            # ------------------------------------------

            schedule_item = (
                session.query(studyScheduleItemDA)
                .filter(
                    studyScheduleItemDA.id == schedule_item_id
                )
                .first()
            )

            if not schedule_item:
                logger.warning(f"Study schedule item not found: "f"{schedule_item_id}")
                return False

            # ------------------------------------------
            # Check book
            # ------------------------------------------

            book = (
                session.query(bookDA)
                .filter( bookDA.id == schedule_item.book_id)
                .first()
            )

            if not book:
                logger.warning(f"Book not found: book_id={schedule_item.book_id}")
                return False


            # ------------------------------------------
            # Study date
            # ------------------------------------------

            if study_date is None:
                study_date = date.today()

            # ------------------------------------------
            # Create study session
            # ------------------------------------------

            study_session = studySessionDA(
                schedule_item_id=schedule_item_id,
                study_date=study_date,
                start_page = start_page,
                end_page = end_page,
                duration_seconds =duration_seconds,
            )

            session.add(study_session)

            # ------------------------------------------
            # Update book current page
            # ------------------------------------------

            if end_page > book.current_page:
                book.current_page = end_page + 1

            # ------------------------------------------
            # Commit
            # ------------------------------------------

            session.commit()

            logger.info(
                "Study session created successfully: "
                f"schedule_item_id={schedule_item_id}, "
                f"completed_pages={end_page - start_page + 1}, "
                f"duration_seconds={duration_seconds}"
            )

            return True

        except Exception as error:
            session.rollback()
            logger.exception(f"Error creating study session: {error}")
            return False

        finally:
            session.close()