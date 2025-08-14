# table_config.py


TABLE_CONFIGS = {
    'Клеверенс_Склад_15_Прайс_лист_28_03_2025_РФ_4.xlsx': {
        'table_name': 'clever_storage',
        'sheet_name': 1,
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
        'sheet_name': 1,
        'columns': ['article', 'license_level', 'configuration', 'short_name', 'price', 'chunk', 'embedding'],
        'chunk': ['license_level', 'configuration'],
        'excel_column_map': {
            "Артикул": "article",
            "Конфигурация 1С": "configuration",
            "Уровень лицензии": "license_level",
            "Короткое наименование\nлицензии Магазин 15 (для заголовков и сайта)": "short_name",
            "Цена розничная,\nбез НДС": "price"
        }
    }
}