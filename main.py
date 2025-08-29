import time
from init_objects import logger
from logger import log_time
from scripts.atol import import_excel_atol
from scripts.cleverens import import_excel_cleverens


def main():
    start_time = time.time()

    import_excel_atol("price_lists/Price ATOL 2025-04-14 (Золото).xlsx")
    import_excel_cleverens("price_lists/Клеверенс_Магазин_15_Прайс_лист_28_03_2025_РФ.xlsx")
    import_excel_cleverens("price_lists/Клеверенс_Склад_15_Прайс_лист_28_03_2025_РФ_4.xlsx")

    log_time(logger, "--- Import process finished. Duration: ", start_time)


if __name__ == "__main__":
    main()