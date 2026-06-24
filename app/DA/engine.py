from sqlalchemy import create_engine
from cmn.config_reader import ConfigReader
from cmn.resource_helper import resource_path
from cmn.path_manager import PathManager

def create_db_engine():
    config_reader = ConfigReader("config.json")
    db_config = config_reader.get("database")
    driver = db_config["driver"]
    
    if driver == 'sqlite':
        dbPath = resource_path(PathManager.DB_PATH, db_config['DBName'])
        connection_string = f"sqlite:///{dbPath}"
    elif driver == 'sqlServer':
        server = db_config['server']
        database = db_config['dBName']
        connection_string = f"mssql+pyodbc://{server}/{database}"
    else:
        raise NotImplementedError(f"Driver {driver} not supported")
    
    return create_engine(connection_string, echo=True)