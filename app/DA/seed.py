from cmn.config_reader import ConfigReader
from sqlalchemy import insert, inspect , MetaData, select
from .base import Base

def Create_SeedData(engine):
    
    data = ConfigReader("seed.json").load()
    loadSeedData = ConfigReader("config.json").get("loadSeedData" , 1 )
    if loadSeedData == 1:
        for table_name, rows in data.items():
            with engine.begin() as conn:
                metadata = Base.metadata
                metadata.reflect(bind=engine, only=[t for t in data.keys() if t not in metadata.tables])
                seed_table(conn, metadata, table_name, rows)
        
        ConfigReader("config.json").set("loadSeedData" , 0 )

def seed_table(conn, metadata, table_name, rows):
    table = metadata.tables[table_name]
    pk_col =  [c for c in table.columns if c.primary_key]
    pk_col = pk_col[0].name

    for row in rows:
        insert_row(row , conn, metadata, table , table_name)

def insert_row(row ,conn, metadata, table , table_name):
    parent_data = {}
    children = {}
    processed_data = {}
    references_to_resolve = {}

    for k, v in row.items():
        if isinstance(v, list):
            children[k] = v
        else:
            parent_data[k] = v
    
    for key, value in parent_data.items():
        if key.endswith('_name'):
            id_field_name = key.replace('_name', '_id')
            references_to_resolve[id_field_name] = value
        else:
            processed_data[key] = value

    for id_field_name, ref_value in references_to_resolve.items():
        ref_id = resolve_reference(conn, metadata, table, id_field_name, ref_value)
        if ref_id is not None:
            processed_data[id_field_name] = ref_id
        else:
            ValueError(f"Value '{ref_value}' not found in the reference table for field '{id_field_name}'")
    try:
        insertTable = insert(table).values(**processed_data)
        result = conn.execute(insertTable)
        parent_id = result.inserted_primary_key[0]
        for child_table_name, child_rows in children.items():
            child_table = metadata.tables.get(child_table_name)
            if child_table is None:
                raise ValueError(f"child table '{child_table_name}' not found")

            fk_col = f"{table_name}_id"

            for child in child_rows:
                child[fk_col] = parent_id
                insert_row(child , conn , metadata , child_table , child_table_name )
                
    except Exception as e:
            print(f"Error insert seed data: {e}")



def resolve_reference(conn, metadata: MetaData, source_table, id_field_name: str, ref_value: str) -> int:
    if hasattr(source_table.c, id_field_name):
        id_column = getattr(source_table.c, id_field_name)
    else:
        for column in source_table.columns:
            if column.name == id_field_name:
                id_column = column
                break
        else:
            raise ValueError(f"Column '{id_field_name}' not found in table '{source_table.name}'")

    if not id_column.foreign_keys:
        raise ValueError(f"Column '{id_field_name}' is not a Foreign Key")
    
    fk = next(iter(id_column.foreign_keys))
    target_table_name = fk.column.table.name
    target_column_name = fk.column.name  
    
    target_table = metadata.tables[target_table_name]

    name_column = None
    for column in target_table.columns:
        if column.name.lower() in ['name', 'title', 'label']:
            name_column = column
            break
    
    if name_column is None:
        raise ValueError(f"Column 'name' not found in table '{target_table_name}'")
    
    stmt = select(target_table.c[target_column_name]).where(name_column == ref_value)
    result = conn.execute(stmt).fetchone()
    
    if result:
        return result[0]
    else:
        insert_stmt = insert(target_table).values({name_column.name: ref_value})
        result = conn.execute(insert_stmt)
        return result.inserted_primary_key[0]