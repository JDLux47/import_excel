import glob
import os
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


load_dotenv()
PG_DSN = os.getenv("PG_DSN")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILES = glob.glob(os.path.join(SCRIPT_DIR, "*.xlsx"))


MODEL_NAME = "intfloat/multilingual-e5-large-instruct"
EMB_SIZE = 1024


model = SentenceTransformer(MODEL_NAME)


engine = create_engine(PG_DSN)
meta = MetaData()
vectors_table = Table(
    "embeddings", meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("embedding", Vector(EMB_SIZE)),
    Column("chunk", String)
)


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


def table_rebuild():
    logger.info("Rebuild database table")
    try:
        vectors_table.drop(engine, checkfirst=True)
        vectors_table.create(engine, checkfirst=True)
    except Exception as e:
        logger.exception("Error updating database %s", e)
        raise


def read_excel_file(file_path, columns):
    logger.info(f"Read excel file: {file_path}")
    try:
        df = pd.read_excel(file_path, sheet_name=1)
        existing_columns = [col for col in columns if col in df.columns]
        df = df[existing_columns].dropna()
        logger.info(f"Data has been read successfully: {len(df)} rows")
        return df, existing_columns
    except Exception as e:
        logger.exception("Error reading file: %s", e)
        return None, []


def create_chunks(df, existing_columns):
    logger.info("Creating chunks")
    chunks = []
    for idx, row in df.iterrows():
        line = "; ".join(str(row[col]) for col in existing_columns)
        chunks.append(line)
    logger.info(f"Chunks have been created. {len(chunks)} chunks")
    return chunks


def vectorize_chunks(chunks):
    logger.info("Vectorizing data %s", MODEL_NAME)
    try:
        embeddings = model.encode(chunks)
        logger.info("The data has been vectorized successfully")
        return embeddings
    except Exception as e:
        logger.exception("Error vectorizing data %s", e)
        return None


def insert_to_db(chunks, embeddings):
    logger.info("Loading data to database")
    try:
        with engine.begin() as conn:
            for chunk, emb in zip(chunks, embeddings):
                conn.execute(vectors_table.insert().values(embedding=emb.tolist(), chunk=chunk))
    except Exception as e:
        logger.exception("Error insert data", e)
        raise


def main():
    start_time = time.time()
    logger.info("----- Start import process -----")
    if not PG_DSN:
        logger.error("Variable PG_DSN not found")
        return
    if not EXCEL_FILES:
        logger.error(f"No Excel files in the folder {SCRIPT_DIR}")
        return

    table_rebuild()

    for file_path in EXCEL_FILES:
        if not os.path.isfile(file_path):
            logger.error(f"File not found: {file_path}")
            continue
        df, existing_columns = read_excel_file(file_path, COLUMNS)
        if df is None or len(df) == 0:
            continue
        chunks = create_chunks(df, existing_columns)
        if not chunks:
            continue
        embeddings = vectorize_chunks(chunks)
        if embeddings is None:
            continue
        insert_to_db(chunks, embeddings)

    end_time = time.time()
    diff_time = end_time - start_time
    logger.info(f"----- Import process finished. Duration: {diff_time} sec -----")


if __name__ == "__main__":
    main()