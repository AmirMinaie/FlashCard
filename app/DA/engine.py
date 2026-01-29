from sqlalchemy import create_engine
from cmn.config_reader import ConfigReader, resource_path

def create_db_engine():
    config_reader = ConfigReader("config.json")
    db_config = config_reader.get("database")
    driver = db_config["driver"]
    
    if driver == 'sqlite':
        DB_PATH = resource_path('app', db_config['DBName'])
        connection_string = f"sqlite:///{DB_PATH}"
    elif driver == 'sqlServer':
        server = db_config['server']
        database = db_config['dBName']
        connection_string = f"mssql+pyodbc://{server}/{database}"
    else:
        raise NotImplementedError(f"Driver {driver} not supported")
    
    return create_engine(connection_string, echo=True)