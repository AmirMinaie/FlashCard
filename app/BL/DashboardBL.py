from dataclasses import dataclass
from sqlalchemy import func, case , or_
from datetime import datetime, timedelta , date
from DA.session import get_session
from DA.models import flashcardDA , fileFlashcardDA , constantDA , reviewFlashcardDA
from cmn.config_reader import ConfigReader
from BL.ReviewBL import ReviewBL

@dataclass
class DashboardSummary:
    today_reviews: int
    remaining_reviews: int
    streak: int
    due_today: int
    today_progress: float

@dataclass
class LearningProgress:
    new_cards: int
    learning_cards: int
    review_cards: int
    mature_cards: int
    total_cards: int
    new_percent : float
    learning_percent : float
    review_percent : float
    mature_percent : float

@dataclass
class UpcomingReview:
    tomorrow: int
    next3: int
    next7: int
    next30: int

@dataclass
class Performance:
    avg_quality : float
    success_rate : float
    avg_total_time : float

@dataclass
class ReviewStats:
    words_read_yesterday: int
    avg_words_reviewed_last_two_weeks: float

class DashboardBL:

    def __init__(self):
        self.today = datetime.now().date()
        Config = ConfigReader()
        self.REVIEW_THRESHOLD = Config.get("REVIEW_THRESHOLD")
        self.MATURE_INTERVAL_DAYS = Config.get("MATURE_INTERVAL_DAYS")
        self.NEW_CARD_TIME = Config.get( "NEW_CARD_TIME")
        self.LEARNING_CARD_TIME = Config.get( "LEARNING_CARD_TIME")
        self.REVIEW_CARD_TIME = Config.get( "REVIEW_CARD_TIME")
        return

    def get_summary(self):

        session = get_session()
        
        today_reviews = (
        ReviewBL.completed_reviews_query( session, self.today, self.today )
        .count()
        )
        
        remaining_reviews = (
            ReviewBL.get_due_cards_query(session)
            .count()
        )
        due_today= remaining_reviews + today_reviews

        today_progress = (
            (today_reviews * 100) / due_today
            if due_today > 0
            else 0
        )
        
        session.close()

        return DashboardSummary(
            today_reviews=today_reviews,
            remaining_reviews= remaining_reviews ,
            streak= self.get_streak(),
            due_today= due_today,
            today_progress = today_progress
        )

    def get_learning_progress(self):
        
        session = get_session()

        active_count = 0

        total_cards = session.query(func.count(flashcardDA.id)).scalar()

        new_cards = (
            session.query(func.count(flashcardDA.id))
            .filter(flashcardDA.last_review_quality == None)
            .scalar()
        )
        
        learning_cards = (
            session.query(func.count(flashcardDA.id))
            .filter(flashcardDA.last_review_quality != None,
                    flashcardDA.last_repetitions < self.REVIEW_THRESHOLD)
            .scalar()
        )

        review_cards = (
            session.query(func.count(flashcardDA.id))
            .filter(flashcardDA.last_repetitions >= self.REVIEW_THRESHOLD,
                    flashcardDA.last_interval < self.MATURE_INTERVAL_DAYS)
            .scalar()
        )

        mature_cards = (
            session.query(func.count(flashcardDA.id))
            .filter(flashcardDA.last_interval >= self.MATURE_INTERVAL_DAYS)
            .scalar()
        )
        
        active_count = new_cards + learning_cards + review_cards

        new_percent = 100*( new_cards / active_count)
        learning_percent = 100*( learning_cards / active_count)
        review_percent = 100*( review_cards / active_count)
        mature_percent = 100*( mature_cards / total_cards)

        session.close()

        return LearningProgress(
            new_cards=new_cards,
            learning_cards= learning_cards,
            review_cards= review_cards,
            mature_cards= mature_cards,
            total_cards= total_cards,
            new_percent= new_percent,
            learning_percent = learning_percent ,
            review_percent = review_percent ,
            mature_percent = mature_percent ,
        )

    def get_upcoming_reviews(self):
        session = get_session()

        tomorrow_count = (ReviewBL.get_due_cards_query( session, next_Day= 1 ).count())
        next3_count =(ReviewBL.get_due_cards_query( session, next_Day= 3 ).count())
        next7_count = (ReviewBL.get_due_cards_query( session, next_Day= 7 ).count())
        next30_count = (ReviewBL.get_due_cards_query( session, next_Day= 30 ) .count() )

        session.close()

        return UpcomingReview(
            tomorrow= tomorrow_count,
            next3=next3_count,
            next7=next7_count,
            next30=next30_count,
        )
    
    def get_streak(self):

        session = get_session()

        review_days = (
            session.query(func.date(reviewFlashcardDA.createAt))
            .distinct()
            .order_by(func.date(reviewFlashcardDA.createAt).desc())
            .all()
        )

        review_days = [r[0] for r in review_days]

        if not review_days:
            return 0

        # اگر امروز مرور نکرده ولی دیروز کرده، استریک از دیروز حساب می‌شود
        if review_days[0] == str(self.today):
            expected = self.today
        elif review_days[0] == str(self.today - timedelta(days=1)):
            expected = self.today - timedelta(days=1)
        else:
            return 0

        streak = 0

        for day in review_days:
            if day == str(expected):
                streak += 1
                expected -= timedelta(days=1)
            else:
                break

        session.close()
        return streak

    def get_global_average_review_time(self, session, limit=1000):
        global_avg = (
            session.query(func.avg(reviewFlashcardDA.total_time))
            .filter(
                reviewFlashcardDA.id.in_(
                    session.query(reviewFlashcardDA.id)
                    .filter(reviewFlashcardDA.total_time.isnot(None))
                    .order_by(reviewFlashcardDA.review_date.desc())
                    .limit(limit)
                )
            )
            .scalar()
        )
        if not global_avg:
            return 60

        return global_avg

    def get_estimated_study_time(self):
        session = get_session()

        due_card_ids = (
            ReviewBL.get_due_cards_query(session)
            .with_entities(flashcardDA.id)
            .all()
        )

        due_card_ids = [card.id for card in due_card_ids]

        if not due_card_ids:
            return 0.0

        card_averages = (
            session.query(
                reviewFlashcardDA.flashcard_id,
                func.avg(reviewFlashcardDA.total_time).label("avg_time"),
                func.count(reviewFlashcardDA.id).label("review_count"),
            )
            .filter(
                reviewFlashcardDA.flashcard_id.in_(due_card_ids),
                reviewFlashcardDA.total_time.isnot(None)
            )
            .group_by(reviewFlashcardDA.flashcard_id)
            .all()
        )

        card_stats = {
            card_id: {"avg": avg_time, "count": review_count}
            for card_id, avg_time, review_count in card_averages
        }

        global_avg = self.get_global_average_review_time(session) or 0

        MIN_REVIEWS = 3
        BUFFER = 1.05

        estimated = 0
        for card_id in due_card_ids:
            if card_id in card_stats and card_stats[card_id]["count"] >= MIN_REVIEWS and card_stats[card_id]["avg"] > 0:
                estimated += card_stats[card_id]["avg"]
            else:
                estimated += global_avg
        estimated = estimated * BUFFER
        return estimated

    def get_performance(self, start_date, end_date):

        session = get_session()

        result = (
            ReviewBL.completed_reviews_query(session, start_date, end_date)
            .with_entities(
                func.avg(reviewFlashcardDA.quality).label("avg_quality"),
                (
                    func.sum(
                        case(
                            (reviewFlashcardDA.quality >= 4, 1),
                            else_=0
                        )
                    ) * 100.0
                    / func.count(reviewFlashcardDA.id)
                ).label("success_rate"),
                func.avg(reviewFlashcardDA.total_time).label("avg_total_time"),
            )
            .one()
        )

        session.close()

        avg_quality = result.avg_quality or 0
        success_rate = result.success_rate or 0
        avg_total_time = result.avg_total_time or 0

        return Performance(
            avg_quality=avg_quality,
            success_rate=success_rate,
            avg_total_time=avg_total_time,
        )

    def get_Review_Stats(self):
        session = get_session()

        yesterday = self.today - timedelta(days=1)
        start_date = self.today - timedelta(days=15)
        end_date = self.today - timedelta(days=2)

        words_read_yesterday = (
            ReviewBL.completed_reviews_query(session, yesterday, yesterday)
            .count()
        )

        daily_reviews = (
            ReviewBL.completed_reviews_query(session, start_date, end_date)
            .with_entities(
                func.date(reviewFlashcardDA.createAt).label("review_date"),
                func.count(reviewFlashcardDA.id).label("review_count"),
            )
            .group_by(func.date(reviewFlashcardDA.createAt))
            .all()
        )


        if daily_reviews:
            total_reviews = sum(review.review_count for review in daily_reviews)
            avg_words_reviewed = total_reviews / 14 
        else:
            avg_words_reviewed = 0

        session.close()

        return ReviewStats(
            words_read_yesterday=words_read_yesterday or 0,
            avg_words_reviewed_last_two_weeks=round(avg_words_reviewed, 1)
        )

    def get_average_daily_time(self, start_date, end_date):

        session = get_session()

        daily_times = (
            ReviewBL.completed_reviews_query(session, start_date, end_date)
            .with_entities(
                func.coalesce(
                    func.sum(reviewFlashcardDA.total_time), 0
                ).label("daily_total")
            )
            .group_by(func.date(reviewFlashcardDA.createAt))
            .having(func.sum(reviewFlashcardDA.total_time) > 0)
            .all()
        )

        session.close()

        if not daily_times:
            return 0

        total = sum(row.daily_total for row in daily_times)

        return total / len(daily_times)