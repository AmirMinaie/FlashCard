from DA.session import get_session
from DA.models import flashcardDA  

class FlashCardBL:
    def __init__(self):
        self.session_factory = get_session()

    def add_card(self, title, type_Id , description , example ):
        session = self.session_factory
        
        card = flashcardDA(title = title,description = description,example = example,type_Id = type_Id)
        session.add(card)
        session.commit()
        id = card.id
        session.close()
        return id

    def get_cards(self):
        session = self.session_factory
        cards = session.query(flashcardDA).all()
        session.close()
        return cards
    
    def get_today_flashcards(self):
        return self.get_cards()

