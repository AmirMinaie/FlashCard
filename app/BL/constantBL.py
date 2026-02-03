from DA.session import get_session
from DA.models import constantDA  

class constantBL:
    def __init__(self):
        self.session_factory = get_session()

    def get_constant(self , constantType):
        session = self.session_factory
        cards = session.query(constantDA).filter(constantDA.type == constantType).all()
        session.close()
        return cards
