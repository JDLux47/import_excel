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

load_dotenv()
PG_DSN = os.getenv("PG_DSN")
FILE_PATH = os.getenv("FILE_PATH")

COLUMNS = [
    "Артикул",
    "Короткое наименование\nлицензии Склад 15  (для заголовков и сайта)",
    "Цена розничная,\nбез НДС"
]

MODEL_NAME = "intfloat/multilingual-e5-large-instruct"
EMB_SIZE = 1024

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


def read_and_import_excel():

    start_time = time.time()
    logger.info("----- start import process -----")

    if not PG_DSN:
        logger.error("variable PG_DSN not found")
        return
    if not FILE_PATH:
        logger.error("variable FILE_PATH not found")
        return
    if not os.path.isfile(FILE_PATH):
        logger.error("file not found: %s", FILE_PATH)
        return

    try:
        engine = create_engine(PG_DSN)
        meta = MetaData()

        vectors_table = Table(
            "embeddings", meta,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("embedding", Vector(EMB_SIZE)),
            Column("chunk", String)
        )

        logger.info("read excel file: %s", FILE_PATH)
        try:
            df = pd.read_excel(FILE_PATH, sheet_name=1)
            df = df[COLUMNS].dropna()
        except Exception as e:
            logger.exception("error reading file: %s", e)
            return
        logger.info("data has been read successfully: %d raws", len(df))

        logger.info("creating chunks")
        chunks = []
        for idx, row in df.iterrows():
            line_parts = []
            for col in COLUMNS:
                value = row[col]
                line_parts.append(f"{value}")
            line = "; ".join(line_parts)
            chunks.append(line)
        logger.info("chunks have been created. %d chunks", len(chunks))

        logger.info("vectorizing data %s", MODEL_NAME)
        try:
            model = SentenceTransformer(MODEL_NAME)
            embeddings = model.encode(chunks)
        except Exception as e:
            logger.exception("error vectorizing data %s", e)
            return
        logger.info("the data has been vectorized successfully")

        logger.info("update database table")
        try:
            vectors_table.drop(engine, checkfirst=True)
            vectors_table.create(engine, checkfirst=True)
        except Exception as e:
            logger.exception("error updating database %s", e)
            return

        try:
            logger.info("loading data to database")
            with engine.begin() as conn:
                for chunk, emb in zip(chunks, embeddings):
                    conn.execute(vectors_table.insert().values(embedding=emb.tolist(), chunk=chunk))
        except Exception as e:
            logger.exception("error insert data", e)

    except Exception as e:
        logger.exception("error import", e)

    end_time = time.time()
    diff_time = end_time - start_time
    logger.info("----- Import process finished. Duration: %.2f секунд -----", diff_time)


if __name__ == "__main__":
    read_and_import_excel()