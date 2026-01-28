from cmn.config_reader import ConfigReader
from DA.session import get_session
from DA.models import *

class seed():
    def __init__(self) -> None:
        self.seed_Data = ConfigReader("seed.json").load()
        self.seed_flashcards()
        self.seed_Constant()

    def seed_Constant(self):
        seedData = self.seed_Data['constants']
        session = get_session()
        if session.query(constantDA).count() > 0:
            session.close()
            return
        constants = [constantDA(**cons) for cons in seedData]
        session.add_all(constants)
        session.commit()
        session.close()
        pass

    def seed_flashcards(self):
        seedData = self.seed_Data['flashcards']
        session = get_session()
        if session.query(flashcardDA).count() > 0:
            session.close()
            return
        constants = [flashcardDA(**cons) for cons in seedData]
        session.add_all(constants)
        session.commit()
        session.close()
