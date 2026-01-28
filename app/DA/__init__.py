from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base
from .models import * 
from cmn.config_reader import ConfigReader , Base_dir , get_dir

config_reader = ConfigReader("config.json")
db_config = config_reader.get("database")
driver = db_config["driver"]
conectionString = ""

if driver == 'sqlite':
    DB_PATH = get_dir( 'app', db_config['DBName'] )
    conectionString = f"sqlite:///{DB_PATH}"

elif driver == 'sqlServer':
    server = db_config['server'] 
    database = db_config['dBName']  
    conectionString = f"mssql+pyodbc://{server}/{database}"
else:
    NotImplementedError

engine = create_engine(conectionString, echo=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

