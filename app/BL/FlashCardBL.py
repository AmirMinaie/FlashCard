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
from cmn.logger import logger
from cmn.config_reader import ConfigReader

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
                 ,level_id
                 ,files
                 ,notion_content = None
                 ,createAt = None
                 ,updatedAt = None
                 ,reviews = None):
        
        file_Manager = FileManager()
        session = get_session()
        saved_files = []

        try:
            if files:
                for file_data in files:
                    source_type = session.query(constantDA).filter(
                        constantDA.id == file_data["from_type_id"]
                    ).first()

                    if source_type is None:
                        raise ValueError("Invalid source type.")

                    file_info = file_Manager.save_file( file_data["value"],file_data["title"] , source_type.name )

                    type_ = session.query(constantDA).filter(constantDA.name == file_info["type_"]).first()

                    if type_ is None:
                        raise ValueError("Invalid file type.")

                    saved_files.append({
                        "title":file_data["title"],
                        "file_info": file_info,
                        "source_type_id": source_type.id,
                        "type_id": type_.id
                    })

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
                        level_id= level_id,
                        notion_content = notion_content,
                        createAt = createAt,
                        updatedAt = updatedAt)
        
            session.add(card)
            session.flush()
        
            if reviews is None:
                reviews = {
                    "quality": None,
                    "ease_factor": SM2Algorithm.INITIAL_EASE,
                    "interval": 1,
                    "repetitions": 0,
                    "review_date": datetime.now()
                }
            review = reviewFlashcardDA(
                flashcard_id=card.id,
                **reviews
            )
            session.add(review)

            for item in saved_files:
                info = item["file_info"]

                session.add(
                    fileFlashcardDA(
                        flashcard_id=card.id,
                        title=item["title"],
                        filePath=info["filePath"],
                        fileName=info["fileName"],
                        fileSize=info["fileSize"],
                        type_id=item["type_id"],
                        sourceType_id=item["source_type_id"]
                    )
                )

            session.commit()

            return { "id": card.id, "title": card.title}
        
        except Exception as e:
            session.rollback()
            logger.error(str(e))

            for item in saved_files:
                try:
                    file_Manager.delete_audio_file(item["file_info"]["filePath"])
                except Exception:
                    pass

            raise
    
        finally:
            session.close()
            
    def get_card_by_id(self , card_id):
        session = get_session()
        card = session.query(flashcardDA).options(
            selectinload(flashcardDA.files)
            .joinedload(fileFlashcardDA.sourceType)
        ).filter(
            flashcardDA.id == card_id
        ).first()
        session.close()
        return card

    def update_card(self, card_id, **data):

        session = get_session()
        file_manager = FileManager()

        saved_files = []          # فایل‌های جدید
        deleted_file_paths = []   # فایل‌های قدیمی که باید بعد از commit حذف شوند

        try:

            card = session.query(flashcardDA).filter(
                flashcardDA.id == card_id
            ).first()

            if card is None:
                return False

            incoming_files = data.get("files", [])


            for file_data in incoming_files:

                if isinstance(file_data.get("id"), int):
                    continue

                source_type = session.query(constantDA).filter(
                    constantDA.id == file_data["from_type_id"]
                ).first()

                if source_type is None:
                    raise ValueError("Invalid source type.")

                file_info = file_manager.save_file( file_data["value"], file_data["title"], source_type.name )

                type_ = session.query(constantDA).filter(
                    constantDA.name == file_info["type_"]
                ).first()

                if type_ is None:
                    raise ValueError("Invalid file type.")

                saved_files.append({
                    "title":file_data.get("title", ""),
                    "file_info": file_info,
                    "source_type_id": source_type.id,
                    "type_id": type_.id
                })

            # -------------------------
            # Update card
            # -------------------------

            card.title = data["title"]
            card.definition = data["definition"]
            card.example = data["example"]
            card.collocation = data["collocation"]
            card.pastParticiple = data["pastParticiple"]
            card.pastTense = data["pastTense"]
            card.pronunciation = data["pronunciation"]
            card.pos_id = data["pos_id"]
            card.type_id = data["type_id"]
            card.box_id = data["box_id"]
            card.level_id = data["level_id"]

            # -------------------------
            # Delete removed files
            # -------------------------

            incoming_existing_ids = {
                f["id"]
                for f in incoming_files
                if isinstance(f.get("id"), int)
            }

            for file_obj in list(card.files):

                if file_obj.id not in incoming_existing_ids:
                    deleted_file_paths.append(file_obj.filePath)
                    session.delete(file_obj)

            # -------------------------
            # Add new files
            # -------------------------

            for item in saved_files:

                info = item["file_info"]

                session.add(
                    fileFlashcardDA(
                        flashcard_id=card.id,
                        title=item["title"],
                        filePath=info["filePath"],
                        fileName=info["fileName"],
                        fileSize=info["fileSize"],
                        type_id=item["type_id"],
                        sourceType_id=item["source_type_id"]
                    )
                )

            session.commit()

            for path in deleted_file_paths:
                try:
                    file_manager.delete_audio_file(path)
                except Exception as e:
                    logger.error(e)

            return {
                "id": card.id,
                "title": card.title
            }

        except Exception as e:

            session.rollback()

            for item in saved_files:
                try:
                    path = item["file_info"]["filePath"]
                    file_manager.delete_audio_file(path)
                except Exception:
                    pass
            raise

        finally:
            session.close()

    def delete_card(self, card_id):
        session = get_session()

        card = session.query(flashcardDA).filter(
            flashcardDA.id == card_id
        ).first()

        if not card:
            session.close()
            return False

        session.delete(card)
        session.commit()
        session.close()

        return True
    
    def get_cards(self , order=None , SearchText='', where=None , exact_search = False, page = 1 , page_size = 20):
        session = get_session()

        query = self._build_cards_query(
            session,
            SearchText,
            where,
            exact_search
        )
        query = query.options(
            selectinload(flashcardDA.pos),
            selectinload(flashcardDA.type_),
            selectinload(flashcardDA.box),
            selectinload(flashcardDA.level),
        )

        order_expressions = self._get_order_expressions(order)
        if order_expressions:
            query = query.order_by(*order_expressions)

        
        query = query.limit(page_size).offset(
            (page-1)*page_size
        )
        cards = query.all()
        session.close()
        return cards

    def get_cards_count(self , order=None , SearchText='', where=None , exact_search = False):
        session = get_session()
        
        query = self._build_cards_query(
            session,
            SearchText,
            where,
            exact_search
        )

        count = query.with_entities(
            func.count(flashcardDA.id)
        ).scalar()

        session.close()
        return count

    def _build_cards_query( self, session, SearchText='', where=None , exact_search = False):

        query = session.query(flashcardDA)
        where_expressions = self._get_where_expressions(where)

        if where_expressions:
            query = query.where(*where_expressions)

        text_expressions = self._get_text_expressions(SearchText, exact_search)

        if text_expressions:
            query = query.where(*text_expressions)

        return query

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
                    selectinload(flashcardDA.files).selectinload(fileFlashcardDA.sourceType),
                ).filter(or_(
                    flashcardDA.last_review_date <= today,
                    flashcardDA.last_review_date == None                  
                )).order_by(func.random()).first()
            session.close()
            return card_data
        
        except Exception as e:
            logger.error(f"Error getting next card for review: {e}")
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
            logger.error(f"Error marking card reviewed: {e}")
            return False

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
            "last_review_quality": flashcardDA.last_review_quality,
            "created_at": getattr(flashcardDA, 'createAt', flashcardDA.id),
            "updated_at": getattr(flashcardDA, 'updatedAt', flashcardDA.id),
        }
        field = field_mapping.get(field_name.lower())

        if field is None:
            raise ValueError(f"Unknown filter field: {field_name}")
    
        return field
    
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

    def _get_text_expressions(self, search_text , exact_search):
        """
        search_text: str
        """
        if not search_text:
            return []

        search_text = f"%{search_text.lower()}%"

        if exact_search:
            return [
                        or_(
                            flashcardDA.title.ilike(search_text),
                            flashcardDA.definition.ilike(search_text),
                            flashcardDA.example.ilike(search_text),
                            flashcardDA.collocation.ilike(search_text),
                        )
                    ]
        else:
            return [flashcardDA.title.ilike(search_text)]

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
        
        if value == "tomorrow_start":
            return datetime.combine(
                today + timedelta(days=1),
                datetime.min.time()
            )
        
        if value == "day_after_tomorrow_start":
            return datetime.combine(
                today + timedelta(days=2),
                datetime.min.time()
            )

        # اگر ISO date فرستاده شد
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return value