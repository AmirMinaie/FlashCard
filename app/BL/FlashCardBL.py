from DA.session import get_session
from DA.models import flashcardDA , fileFlashcardDA , constantDA , reviewFlashcardDA
from sqlalchemy.orm import selectinload
from dataclasses import dataclass
from typing import List, Optional
from sqlalchemy import asc, desc, and_, or_
from  BL.fileManager import FileManager
from sqlalchemy import func
from datetime import datetime, date , timedelta
from .SM2Algorithm import SM2Algorithm

@dataclass
class OrderByConfig:
    field: str
    direction: str = "asc"  # asc یا desc
    
    def is_valid(self):
        return self.direction.lower() in ["asc", "desc"]

class FlashCardBL:
    def add_card(self
                 ,title
                 ,definition
                 ,example
                 ,collocation
                 ,pastParticiple
                 ,pastTense
                 ,pronunciation
                 ,pos_id
                 ,type_id
                 ,box_id
                 ,level_id,
                 files):
        filManager = FileManager()
        session = get_session()
        
        
        card = flashcardDA(
                        title= title ,
                        definition= definition,
                        example= example,
                        collocation= collocation,
                        pastParticiple= pastParticiple,
                        pastTense= pastTense,
                        pronunciation= pronunciation,
                        pos_id= pos_id,
                        type_id= type_id,
                        box_id= box_id,
                        level_id= level_id)
        session.add(card)
        session.flush()

        review = reviewFlashcardDA(
            flashcard_id = card.id ,
            quality = None,
            ease_factor = SM2Algorithm.INITIAL_EASE,
            interval = 1,
            repetitions = 0, 
            review_date = datetime.now()
        )
        session.add(review)

        if files:
            for file in files:
                try:
                    sourceType = session.query(constantDA).where(constantDA.id == file['from_type_Id']).first()
                    fileInfo = filManager.save_file( file['value'] ,sourceType.name)
                    type_ = session.query(constantDA).where(constantDA.name == fileInfo['type_']).first()

                    file = fileFlashcardDA(
                        flashcard_id = card.id ,
                        filePath = fileInfo['filePath'],
                        fileName = fileInfo['fileName'] ,
                        fileSize = fileInfo['fileSize'] ,
                        type_id = type_.id ,
                        sourceType_id = sourceType.id
                    )
                    session.add(file)
                except Exception as e:
                    print(e)

        session.commit()
        card_saved ={"id":card.id , "title":card.title}
        session.close()
        return card_saved

    def get_cards(self , order = None , SearchText = '',where = None ):
        session = get_session()
        query = session.query(flashcardDA).options(
            selectinload(flashcardDA.pos),
            selectinload(flashcardDA.type_),
            selectinload(flashcardDA.box),
            selectinload(flashcardDA.level),
        )
        order_expressions= self._get_order_expressions(order)
        if order_expressions:
            query = query.order_by(*order_expressions)
        
        where_expressions= self._get_where_expressions(where)
        if order_expressions:
            query = query.where(*where_expressions)
        
        text_expressions= self._get_text_expressions(SearchText)
        if order_expressions:
            query = query.where(*text_expressions)
        

        cards= query.all()
        session.close()
        return cards
    
    def get_next_card_for_review(self):
        try:
            session = get_session()
            today = date.today()
            
            card_data = session.query(flashcardDA).\
                options(
                    selectinload(flashcardDA.pos),
                    selectinload(flashcardDA.type_),
                    selectinload(flashcardDA.box),
                    selectinload(flashcardDA.level),
                    selectinload(flashcardDA.files),
                ).filter(or_(
                    flashcardDA.last_review_date <= today,
                    flashcardDA.last_review_date == None                  
                )).order_by(func.random()).first()
            session.close()
            return card_data
        
        except Exception as e:
            print(f"Error getting next card for review: {e}")
            return None

    def mark_card_reviewed(self, card_id, quality_Answer):
        try:
            session=get_session()
            if last_review := session.query(reviewFlashcardDA).\
            where(reviewFlashcardDA.flashcard_id == card_id).\
            order_by(desc(reviewFlashcardDA.updatedAt)).first():

                reviewCalc = SM2Algorithm.calculate_review(
                current_ease=last_review.ease_factor,
                current_interval=last_review.interval,
                current_repetitions=last_review.repetitions,
                quality=quality_Answer
            )
            else:
                reviewCalc = SM2Algorithm.calculate_review(
                    current_ease=2.5,
                    current_interval=0,
                    current_repetitions=0,
                    quality=quality_Answer
                )

            reviewCard = reviewFlashcardDA(
                    flashcard_id = card_id,
                    quality = quality_Answer,
                    ease_factor = reviewCalc['ease_factor'],
                    interval = reviewCalc['interval'],
                    repetitions = reviewCalc['repetitions'],
                    review_date = reviewCalc['next_review'],
            )

            session.add(reviewCard)
            session.commit()
            review_card_saved ={"id":reviewCard.id , "review_date":reviewCard.review_date}
            session.close()
            return review_card_saved
            
        except Exception as e:
            print(f"Error marking card reviewed: {e}")
            return False
    
    def get_today_review_count(self):
        """گرفتن تعداد مرورهای امروز"""
        try:
            today = date.today()
            session = get_session()
            count = session.query(func.count(flashcardDA.id)).\
                filter(or_(
                    flashcardDA.last_review_date <= today,
                    flashcardDA.last_review_date == None                  
                )).scalar()
            session.close()
            if count:
                return count
            return 0
            
        except Exception as e:
            print(f"Error getting today's review count: {e}")
            return 0

    def _get_field(self, field_name):
        field_mapping = {
            "id": flashcardDA.id,
            "title": flashcardDA.title,
            "definition": flashcardDA.definition,
            "example": flashcardDA.example,
            "collocation": flashcardDA.collocation,
            "past_participle": flashcardDA.pastParticiple,
            "past_tense": flashcardDA.pastTense,
            "pronunciation": flashcardDA.pronunciation,
            "pos_id": flashcardDA.pos_id,
            "type_id": flashcardDA.type_id,
            "box_id": flashcardDA.box_id,
            "level_id": flashcardDA.level_id,
            "last_review_date":flashcardDA.last_review_date,
            "created_at": getattr(flashcardDA, 'createAt', flashcardDA.id),
            "updated_at": getattr(flashcardDA, 'updatedAt', flashcardDA.id),
        }
        return field_mapping.get(field_name.lower(), flashcardDA.id)
    
    def _get_order_expressions(self, order):
        """
        order: list[dict] | None
        """
        if not order:
            return []

        expressions = []
        for item in order:
            field = self._get_field(item.get("field"))
            direction = item.get("direction", "asc").lower()

            if direction == "desc":
                expressions.append(desc(field))
            else:
                expressions.append(asc(field))

        return expressions

    def _get_where_expressions(self, where):
        if not where:
            return []

        expressions = []

        for item in where:
            field = self._get_field(item.get("field"))
            op = item.get("op")
            value = self._normalize_where_value(item.get("value"))

            if op == "eq":
                expressions.append(field == value)

            elif op == "ne":
                expressions.append(field != value)

            elif op == "gt":
                expressions.append(field > value)

            elif op == "gte":
                expressions.append(field >= value)

            elif op == "lt":
                expressions.append(field < value)

            elif op == "lte":
                expressions.append(field <= value)

            elif op == "like":
                expressions.append(field.ilike(f"%{value}%"))

            elif op == "in" and isinstance(value, list):
                expressions.append(field.in_(value))

            elif op == "is_null":
                expressions.append(field.is_(None))

            elif op == "is_not_null":
                expressions.append(field.is_not(None))

        return expressions

    def _get_text_expressions(self, search_text):
        """
        search_text: str
        """
        if not search_text:
            return []

        search_text = f"%{search_text}%"

        return [
            or_(
                flashcardDA.title.ilike(search_text),
                flashcardDA.definition.ilike(search_text),
                flashcardDA.example.ilike(search_text),
                flashcardDA.collocation.ilike(search_text),
            )
        ]

    def _normalize_where_value(self, value):
        """
        تبدیل value های semantic به date/datetime
        """
        if not isinstance(value, str):
            return value

        today = date.today()

        if value == "today":
            return today

        if value == "tomorrow":
            return today + timedelta(days=1)

        if value == "yesterday":
            return today - timedelta(days=1)

        if value == "today_start":
            return datetime.combine(today, datetime.min.time())

        if value == "today_end":
            return datetime.combine(today, datetime.max.time())

        # اگر ISO date فرستاده شد
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return value

    def get_today_reviewed_count(self):
        try:
            today = date.today()
            session = get_session()
            count = session.query(func.count(flashcardDA.id)).\
                filter(func.date(flashcardDA.last_reviewed_date) == today).scalar()
            session.close()
            return count or 0
            
        except Exception as e:
            print(f"Error getting today's review count: {e}")
            return 0
