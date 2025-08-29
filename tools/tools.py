import pandas as pd
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Table
from init_objects import model, engine, meta, EMB_SIZE, logger


# Возвращаем объект Column в зависимости от имени столбца
def get_column_type(colname):
    if colname == 'id':
        return Column(colname, Integer, primary_key=True, autoincrement=True)
    elif colname == 'embedding':
        return Column(colname, Vector(EMB_SIZE))
    elif colname == 'price':
        return Column(colname, String)
    else:
        return Column(colname, String)


# Создаем табилицу с колонками из конфига и добавляем id
def create_table_from_config(table_name, columns):
    if 'id' not in columns:
        columns = ['id'] + columns
    cols = [get_column_type(col) for col in columns]
    return Table(table_name, meta, *cols)


# Удаляем пробелы в начале и конце строк у переданных столбцов
def strip_selected_columns(df, columns):
    for col in columns:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df


# Переименоваем столбцы по словарю из конфига
def rename_columns(df, col_map):
    logger.info(f"Rename columns according to: {col_map}")
    return df.rename(columns=col_map)


# Очищаем датафрейм от лишних столбцов, оставляем только те, которые есть словаре
def select_final_columns(df, columns):
    selected = [col for col in columns if col in df.columns]
    logger.info(f"Summary columns: {selected}")
    return df[selected]


# Откидываем строки, где нет price
def filter_rows_with_price(df):
    mask = df['price'].notnull() & (df['price'].astype(str).str.strip() != '')
    return df[mask]


# Записываем данные из датафрейма в таблицу базы данных
def insert_into_db(table, df, columns):
    logger.info(f"Write {len(df)} rows in table {table.name}")
    records = df[[col for col in columns if col in df.columns] + ['chunk', 'embedding']].to_dict(orient='records')
    with engine.begin() as conn:
        conn.execute(table.insert(), records)
    logger.info("Data has been successfully recorded")


# Читаем файл и возвращаем датафрейм с указанными полями
def read_excel_file(excel_path, sheet_name, used_columns, header):
    logger.info(f"Read excel file {excel_path} (sheet: {sheet_name})")
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header)
    available_columns = [col for col in used_columns if col in df.columns]
    df = df[available_columns]
    logger.info(f"Found {len(available_columns)} necessary columns: {available_columns}")
    return df