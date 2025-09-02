import pandas as pd
from init_objects import model, logger


# Создаём колонку чанк из полей указанных в конфиге
def make_chunk(row, chunk_fields):
    return " ".join(str(row[field]) for field in chunk_fields if field in row.index and pd.notnull(row[field]))


# Добавляем в датафрейм столбец chunk
def add_chunk_column(df, chunk_fields):
    logger.info(f"Create column 'chunk' from fields: {chunk_fields}")
    df['chunk'] = df.apply(lambda row: make_chunk(row, chunk_fields), axis=1)
    logger.info("Column 'chunk' successfully added")
    return df


# Добавляем в датафрейм столбец с векторным представлением
def add_embedding(df):
    logger.info("Vectorizing chunks, count: %d", len(df))
    embeddings = model.encode(df['chunk'].tolist())
    df['embedding'] = [emb.tolist() for emb in embeddings]
    logger.info("Column 'embedding' successfully added")
    return df