from DA.session import get_session
from DA.models import constantDA  

class constantBL:
    def __init__(self):
        self.session_factory = get_session()

    def get_constant(self , constantType):
        session = self.session_factory
        constant = session.query(constantDA).filter(constantDA.type == constantType).all()
        session.close()
        return constant

    def get_constant_name(self , name):
        session = self.session_factory
        constant = session.query(constantDA).\
            filter(constantDA.name == name).first()
        session.close()
        return constant
