import glob
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, MetaData

from logger import setup_logger

load_dotenv()
PG_DSN = os.getenv("PG_DSN")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILES = glob.glob(os.path.join(SCRIPT_DIR, "price_lists/*.xlsx"))

MODEL_NAME = "intfloat/multilingual-e5-base"
EMB_SIZE = 768

model = SentenceTransformer(MODEL_NAME)

engine = create_engine(PG_DSN)
meta = MetaData()

logger = setup_logger()