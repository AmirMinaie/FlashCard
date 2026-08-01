from datetime import datetime, timedelta , date
from DA.models import flashcardDA , fileFlashcardDA , reviewFlashcardDA
from sqlalchemy import func, case , or_

class ReviewBL:

    @staticmethod
    def get_due_cards_query(session):
        today = date.today()

        return (
            session.query(flashcardDA)
            .filter(
                or_(
                    flashcardDA.last_review_date <= today,
                    flashcardDA.last_review_date.is_(None)
                )
            )
        )

    @staticmethod
    def completed_reviews_query(session, start_date=None, end_date=None):

        query = (
            session.query(reviewFlashcardDA)
            .filter(
                reviewFlashcardDA.quality.isnot(None),
                reviewFlashcardDA.quality != -1
            )
        )

        if start_date is not None:
            query = query.filter(
                func.date(reviewFlashcardDA.createAt) >= start_date
            )

        if end_date is not None:
            query = query.filter(
                func.date(reviewFlashcardDA.createAt) <= end_date
            )

        return query