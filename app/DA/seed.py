from cmn.config_reader import ConfigReader
from sqlalchemy import insert, inspect , MetaData, select
from .base import Base

def Create_SeedData(engine):
    
    data = ConfigReader("seed.json").load()
    for table_name, rows in data.items():
        with engine.begin() as conn:
            metadata = Base.metadata
            metadata.reflect(bind=engine, only=[t for t in data.keys() if t not in metadata.tables])
            seed_table(conn, metadata, table_name, rows)

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
            raise ValueError(f"مقدار '{ref_value}' در جدول reference برای فیلد '{id_field_name}' یافت نشد")

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
        # اگر نام دقیق ستون را نداریم، به دنبالش بگردیم
        for column in source_table.columns:
            if column.name == id_field_name:
                id_column = column
                break
        else:
            raise ValueError(f"ستون '{id_field_name}' در جدول '{source_table.name}' یافت نشد")
    
    # بررسی اینکه آیا این ستون Foreign Key است
    if not id_column.foreign_keys:
        raise ValueError(f"ستون '{id_field_name}' یک Foreign Key نیست")
    
    # گرفتن اطلاعات جدول مقصد از اولین foreign key
    fk = next(iter(id_column.foreign_keys))
    target_table_name = fk.column.table.name
    target_column_name = fk.column.name  # معمولاً 'id'
    
    # پیدا کردن جدول مقصد
    target_table = metadata.tables[target_table_name]
    
    # پیدا کردن ستون name در جدول مقصد
    # فرض می‌کنیم ستون 'name' وجود دارد
    name_column = None
    for column in target_table.columns:
        if column.name.lower() in ['name', 'title', 'label']:
            name_column = column
            break
    
    if name_column is None:
        raise ValueError(f"ستون 'name' در جدول '{target_table_name}' یافت نشد")
    
    # جستجو در جدول مقصد بر اساس نام
    stmt = select(target_table.c[target_column_name]).where(name_column == ref_value)
    result = conn.execute(stmt).fetchone()
    
    if result:
        return result[0]
    else:
        # اگر پیدا نشد، رکورد جدید ایجاد کن
        insert_stmt = insert(target_table).values({name_column.name: ref_value})
        result = conn.execute(insert_stmt)
        return result.inserted_primary_key[0]