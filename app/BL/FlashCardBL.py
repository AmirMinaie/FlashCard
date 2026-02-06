from DA.session import get_session
from DA.models import flashcardDA , fileFlashcardDA , constantDA , reviewFlashcardDA
from sqlalchemy.orm import selectinload
from dataclasses import dataclass
from typing import List, Optional
from sqlalchemy import asc, desc, and_, or_
from  BL.fileManager import FileManager
from sqlalchemy import func
from datetime import datetime, date
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

    def get_cards(self , order_config: Optional[list[OrderByConfig]] = None):
        session = get_session()
        query = session.query(flashcardDA).options(
            selectinload(flashcardDA.pos),
            selectinload(flashcardDA.type_),
            selectinload(flashcardDA.box),
            selectinload(flashcardDA.level),
        )
        order_expressions= self._get_order_expressions(order_config)
        if order_expressions:
            query = query.order_by(*order_expressions)

        cards= query.all()
        session.close()
        return cards
    
    def get_next_card_for_review(self):
        try:
            session = get_session()
            card_data = self._get_query_review_today(session).\
            order_by(func.random()).\
            first()
            session.close()
            return card_data
        
        except Exception as e:
            print(f"Error getting next card for review: {e}")
            return None

    def mark_card_reviewed(self, card_id, quality_Answer):
        try:
            session=get_session()
            laste_review = session.query(reviewFlashcardDA).\
                where(reviewFlashcardDA.flashcard_id == card_id).\
                order_by(desc(reviewFlashcardDA.updatedAt)).first()
            
            reviewCalc = SM2Algorithm.calculate_review(
                current_ease= laste_review.ease_factor,
                current_interval=laste_review.interval,
                current_repetitions=laste_review.repetitions,
                quality= quality_Answer
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
            session = get_session()
            query = self._get_query_review_today(session)
            count = session.query(func.count('*')).\
                select_from(query.subquery()).scalar()
            session.close()
            if count:
                return count
            return 0
            
        except Exception as e:
            print(f"Error getting today's review count: {e}")
            return 0

    def _get_order_field(self, field_name):
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
            "created_at": getattr(flashcardDA, 'created_at', flashcardDA.id),
            "updated_at": getattr(flashcardDA, 'updated_at', flashcardDA.id),
        }
        return field_mapping.get(field_name.lower(), flashcardDA.id)

    def _get_order_expressions(self , order_config):
        order_expressions= []
        if order_config:
            for order in order_config:
                if order.is_valid():
                    field = self._get_order_field(order.field )
                    if order.direction.lower() == 'desc':
                        order_expressions.append(desc(field))
                    else:
                        order_expressions.append(asc(field))
        return order_expressions

    def _get_query_review_today(self , session ):
        today = date.today()
        query = session.query(flashcardDA).options(
            selectinload(flashcardDA.pos),
            selectinload(flashcardDA.type_),
            selectinload(flashcardDA.box),
            selectinload(flashcardDA.level),
            selectinload(flashcardDA.files),
            ).where(
                 func.date(reviewFlashcardDA.review_date) <= today
                )
        return query