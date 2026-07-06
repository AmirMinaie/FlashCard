from dataclasses import dataclass
from sqlalchemy import func, case
from datetime import datetime, timedelta
from DA.session import get_session
from DA.models import flashcardDA , fileFlashcardDA , constantDA , reviewFlashcardDA
from cmn.config_reader import ConfigReader

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
class TodayPerformance:
    average_quality: float
    success_rate: float

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
            session.query(func.count(reviewFlashcardDA.id))
            .filter(
                func.date(reviewFlashcardDA.createAt) == self.today,
                reviewFlashcardDA.quality.isnot(None)
            )
            .scalar()
        )
        
        remaining_reviews = (
            session.query(func.count(flashcardDA.id))
            .filter(
                flashcardDA.last_review_date <= datetime.now()
            )
            .scalar()
        )
        due_today= remaining_reviews + today_reviews

        today_progress = (today_reviews * 100) / due_today
        
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

        tomorrow = datetime.combine(self.today + timedelta(days=1), datetime.max.time())
        next3_end = datetime.combine(self.today + timedelta(days=3), datetime.max.time())
        next7_end = datetime.combine(self.today + timedelta(days=7), datetime.max.time())
        next30_end = datetime.combine(self.today + timedelta(days=30), datetime.max.time())
        

        tomorrow_count = (
            session.query(func.count(flashcardDA.id))
            .filter(func.date(flashcardDA.last_review_date) <= tomorrow)
            .scalar()
        )


        next3_count = (
            session.query(func.count(flashcardDA.id))
            .filter(flashcardDA.last_review_date <= next3_end)
            .scalar()
        )

        next7_count = (
            session.query(func.count(flashcardDA.id))
            .filter(flashcardDA.last_review_date <= next7_end)
            .scalar()
        )

        next30_count = (
            session.query(func.count(flashcardDA.id))
            .filter(flashcardDA.last_review_date <= next30_end)
            .scalar()
        )


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
            session.query(
                func.date(reviewFlashcardDA.createAt)
            )
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
    
    def get_estimated_study_time(self):
        session = get_session()

        now = datetime.now()

        new_due = (
            session.query(func.count(flashcardDA.id))
            .filter(
                flashcardDA.last_review_date <= now,
                flashcardDA.last_review_quality.is_(None)
            )
            .scalar()
        )

        learning_due = (
            session.query(func.count(flashcardDA.id))
            .filter(
                flashcardDA.last_review_date <= now,
                flashcardDA.last_review_quality.isnot(None),
                flashcardDA.last_repetitions < self.REVIEW_THRESHOLD
            )
            .scalar()
        )

        review_due = (
            session.query(func.count(flashcardDA.id))
            .filter(
                flashcardDA.last_review_date <= now,
                flashcardDA.last_repetitions >= self.REVIEW_THRESHOLD
            )
            .scalar()
        )

        session.close()

        estimated_seconds = (
            new_due * self.NEW_CARD_TIME +
            learning_due * self.LEARNING_CARD_TIME +
            review_due * self.REVIEW_CARD_TIME
        )

        return estimated_seconds
    
    def get_today_performance(self):

        session = get_session()

        result = (
            session.query(
                func.round( func.avg(reviewFlashcardDA.quality), 2 ).label("average_quality"),

                func.round(
                    (
                        func.sum(
                            case( (reviewFlashcardDA.quality >= 4, 1), else_=0)
                        ) * 100.0
                        / func.count(reviewFlashcardDA.id)
                    ),
                    1
                ).label("success_rate")
            )
            .filter(func.date(reviewFlashcardDA.createAt) == self.today)
            .one()
        )

        session.close()

        return TodayPerformance(
            average_quality=result.average_quality or 0,
            success_rate=result.success_rate or 0,
        )