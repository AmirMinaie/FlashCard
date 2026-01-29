from DA.session import get_session
from DA.models import flashcardDA 
from sqlalchemy.orm import selectinload

class FlashCardBL:
    def add_card(self, title, type_Id , description , example ):
        session = self.session_factory
        
        card = flashcardDA(title = title,description = description,example = example,type_Id = type_Id)
        session.add(card)
        session.commit()
        id = card.id
        session.close()
        return id

    def get_cards(self):
        session = get_session()
        cards = session.query(flashcardDA).options(
            selectinload(flashcardDA.pos),
            selectinload(flashcardDA.type_),
            selectinload(flashcardDA.box),
            selectinload(flashcardDA.level),
        ).all()
        session.close()
        return cards
    
    def get_today_flashcards(self):
        return self.get_cards()

