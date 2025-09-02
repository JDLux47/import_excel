import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, PointStruct, Distance
from init_objects import logger

load_dotenv()
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")


# Добавление в базу qdrant данных из датафрейма
def insert_into_qdrant(collection_name, df, columns, host=HOST, port=PORT, batch_size=500):
    logger.info(f"Upsert {len(df)} rows to Qdrant collection '{collection_name}'")
    dim = len(df.iloc[0]['embedding'])
    client = QdrantClient(host=host, port=port)

    if not client.collection_exists(collection_name=collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
        )

    num_rows = len(df)
    for start in range(0, num_rows, batch_size):
        end = min(start + batch_size, num_rows)
        points = []
        for idx, row in df.iloc[start:end].iterrows():
            payload = {col: row[col] for col in columns if col in row}
            payload['chunk'] = row['chunk']
            point = PointStruct(id=int(idx), vector=row['embedding'], payload=payload)
            points.append(point)
        client.upsert(collection_name=collection_name, points=points)
        logger.info(f"Upserted points {start} to {end} into Qdrant")

    logger.info("Data has been successfully upserted into Qdrant")