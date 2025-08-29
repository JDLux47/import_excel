import logging
import os
from datetime import datetime
import time


# Кастомный логгер
def setup_logger():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Формируем уникальное имя файла по дате и времени запуска (до секунды)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_dir, f"app_{timestamp}.log")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(formatter)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(handler)
    return logger


# Функция для логирования времени событий
def log_time(logger, message, start_time):
    elapsed = time.time() - start_time
    logger.info(f"{message} - {elapsed:.2f} sec")