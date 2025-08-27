import glob
import os
import re
import time
import openpyxl
import psycopg2
from sentence_transformers import SentenceTransformer
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from pgvector.sqlalchemy import Vector
import logging
from columns import COLUMNS
from table_config import TABLE_CONFIGS
from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsNERTagger, Doc

segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
ner_tagger = NewsNERTagger(emb)

load_dotenv()
PG_DSN = os.getenv("PG_DSN")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILES = glob.glob(os.path.join(SCRIPT_DIR, "*.xlsx"))

MODEL_NAME = "intfloat/multilingual-e5-base"
EMB_SIZE = 768

model = SentenceTransformer(MODEL_NAME)

engine = create_engine(PG_DSN)
meta = MetaData()

LOG_FILENAME = os.path.join(os.path.dirname(__file__), 'script.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def detect_device_types_natasha(text, allowed_types):
    text_lower = text.lower()
    found_types = []
    for dev_type in allowed_types:
        if not dev_type:
            continue
        dev_type_low = re.escape(dev_type.lower())
        # паттерн откидывает параметры, которые находятся внутри других слов. Например, касса в слове инкассация
        pattern = r'(?<![a-zа-яё]){}'.format(dev_type_low)
        if re.search(pattern, text_lower, re.IGNORECASE):
            found_types.append(dev_type)
    return ', '.join(found_types) if found_types else ""


def add_parameters_column(df, types):
    logger.info(f"Find types by Natasha from: {types}")
    df['parameters'] = df['chunk'].apply(
        lambda x: detect_device_types_natasha(str(x) if x is not None else '', types)
    )
    logger.info("Column 'parameters' created.")
    return df


def get_column_type(colname):
    if colname == 'id':
        return Column(colname, Integer, primary_key=True, autoincrement=True)
    elif colname == 'embedding':
        return Column(colname, Vector(EMB_SIZE))
    elif colname == 'price':
        return Column(colname, String)
    else:
        return Column(colname, String)


def create_table_from_config(table_name, columns):
    if 'id' not in columns:
        columns = ['id'] + columns
    cols = [get_column_type(col) for col in columns]
    return Table(table_name, meta, *cols)


def make_chunk(row, chunk_fields):
    return " ".join(str(row[field]) for field in chunk_fields if field in row.index and pd.notnull(row[field]))


def strip_selected_columns(df, columns):
    for col in columns:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df


# Находим строку подзаголовок (где заполнено только одно поле)
def detect_category_rows(df, category_col_candidates):
    mask = df.apply(lambda row: (row.notnull() & (row.astype(str).str.strip() != '')).sum() == 1, axis=1)
    empty_df = df.where(~mask, other='')
    cat_series = df[mask].bfill(axis=1).iloc[:, 0]
    series = pd.Series(index=df.index, dtype='object')
    series.loc[cat_series.index] = cat_series.values
    return series


# Добавляем столбец category с последним встреченным подзаголовком и удаляем подзаголовк из датафрейма
def fill_category_column(df):
    # Находим кандидатов: строки, в которых только одна ячейка непуста
    cat_series = detect_category_rows(df, df.columns)
    # Заполняем вниз
    cat_filled = cat_series.fillna(method='ffill')
    # Добавляем колонку категории
    df['category'] = cat_filled
    # Убираем сами строки-подзаголовки (теперь они отмечены только в cat_series)
    df = df[cat_series.isnull()]
    return df


def read_excel_file(excel_path, sheet_name, used_columns, header):
    logger.info(f"Read excel file {excel_path} (sheet: {sheet_name})")
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header)
    available_columns = [col for col in used_columns if col in df.columns]
    df = df[available_columns]
    logger.info(f"Found {len(available_columns)} necessary columns: {available_columns}")
    return df


def rename_columns(df, col_map):
    logger.info(f"Rename columns according to: {col_map}")
    return df.rename(columns=col_map)


def select_final_columns(df, columns):
    selected = [col for col in columns if col in df.columns]
    logger.info(f"Summary columns: {selected}")
    return df[selected]


# откидываем строки, где нет price
def filter_rows_with_price(df):
    mask = df['price'].notnull() & (df['price'].astype(str).str.strip() != '')
    return df[mask]


def add_chunk_column(df, chunk_fields):
    logger.info(f"Create column 'chunk' from fields: {chunk_fields}")
    df['chunk'] = df.apply(lambda row: make_chunk(row, chunk_fields), axis=1)
    logger.info("Column 'chunk' successfully added")
    return df


def add_embedding(df):
    logger.info("Vectorizing chunks, count: %d", len(df))
    embeddings = model.encode(df['chunk'].tolist())
    df['embedding'] = list(embeddings)
    logger.info("Column 'embedding' successfully added")
    return df


def insert_into_db(table, df, columns):
    logger.info(f"Write {len(df)} rows in table {table.name}")
    records = df[[col for col in columns if col in df.columns] + ['chunk', 'embedding']].to_dict(orient='records')
    with engine.begin() as conn:
        conn.execute(table.insert(), records)
    logger.info("Data has been successfully recorded")


def import_excel_to_table(excel_path, table_config):
    table_name = table_config['table_name']
    columns = table_config['columns']
    chunk_fields = table_config['chunk']
    sheet_name = table_config.get('sheet_name')
    col_map = table_config['excel_column_map']
    header_num = table_config['header']
    types = table_config.get('types')

    # Добавим новую колонку заранее, если ее нет
    if 'category' not in columns:
        columns = columns + ['category']
    if types and "parameters" not in columns:
        columns = columns + ["parameters"]

    table = create_table_from_config(table_name, columns)
    table.drop(engine, checkfirst=True)
    table.create(engine, checkfirst=True)

    for sheet in sheet_name:
        df = read_excel_file(excel_path, sheet, COLUMNS, header_num)
        # 1. Добавляем колонку category из подзаголовков, удаляя сами подзаголовки
        df = fill_category_column(df)
        # 2. Приводим к нужным столбцам, далее все шаги как раньше
        df = rename_columns(df, col_map)
        df = strip_selected_columns(df, col_map.values())
        df = filter_rows_with_price(df)
        df = select_final_columns(df, columns)
        df = add_chunk_column(df, chunk_fields)
        df = add_embedding(df)
        if types:
            df = add_parameters_column(df, types)
        insert_into_db(table, df, columns)


def main():
    start_time = time.time()

    for excel_path in EXCEL_FILES:
        filename = os.path.basename(excel_path)
        table_config = TABLE_CONFIGS.get(filename)
        if not table_config:
            logger.warning(f"No table config for {filename}, skipping.")
            continue
        try:
            import_excel_to_table(excel_path, table_config)
        except Exception as e:
            logger.exception(f"Error processing {filename}: {e}")

    diff_time = time.time() - start_time
    logger.info(f"--- Import process finished. Duration: {diff_time:.1f} sec ---")


if __name__ == "__main__":
    main()