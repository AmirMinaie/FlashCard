from DA.session import get_session
from DA.models import flashcardDA 
from sqlalchemy.orm import selectinload
from dataclasses import dataclass
from typing import List, Optional
from sqlalchemy import asc, desc, and_, or_

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
                 ,level_id):
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
        if order_config:
            order_expressions= []
            for order in order_config:
                if order.is_valid():
                    field = self._get_order_field(order.field )
                    if order.direction.lower() == 'desc':
                        order_expressions.append(desc(field))
                    else:
                        order_expressions.append(asc(field))
            if order_expressions:
                query = query.order_by(*order_expressions)


        cards= query.all()
        session.close()
        return cards
    
    def get_today_flashcards(self):
        return self.get_cards()

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

