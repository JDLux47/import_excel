# table_config.py


TABLE_CONFIGS = {
    'Клеверенс_Склад_15_Прайс_лист_28_03_2025_РФ_4.xlsx': {
        'table_name': 'clever_storage',
        'sheet_name': [1],
        'header': 0,
        'columns': ['article', 'license_level', 'configuration', 'short_name', 'price', 'chunk', 'embedding'],
        'chunk': ['license_level', 'configuration'],
        'excel_column_map': {
            "Артикул": "article",
            "Конфигурация 1С": "configuration",
            "Уровень лицензии": "license_level",
            "Короткое наименование\nлицензии Склад 15  (для заголовков и сайта)": "short_name",
            "Цена розничная,\nбез НДС": "price"
        }
    },
    'Клеверенс_Магазин_15_Прайс_лист_28_03_2025_РФ.xlsx': {
        'table_name': 'clever_shop',
        'sheet_name': [1],
        'header': 0,
        'columns': ['article', 'license_level', 'configuration', 'short_name', 'price', 'chunk', 'embedding'],
        'chunk': ['license_level', 'configuration'],
        'excel_column_map': {
            "Артикул": "article",
            "Конфигурация 1С": "configuration",
            "Уровень лицензии": "license_level",
            "Короткое наименование\nлицензии Магазин 15 (для заголовков и сайта)": "short_name",
            "Цена розничная,\nбез НДС": "price"
        }
    },
    'Price ATOL 2025-04-14 (Золото).xlsx': {
        'table_name': 'atol_price',
        'sheet_name': [0,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
        'header': 10,
        'columns': ['article', 'short_name', 'rrc_price', 'price', 'chunk', 'embedding'],
        'chunk': ['short_name'],
        'excel_column_map': {
            "Код": "article",
            "Товар": "short_name",
            "Розничная цена": "rrc_price",
            "Золото": "price"
        }
    }
}