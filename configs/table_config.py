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
        'columns': ['article', 'short_name', 'category', 'rrc_price', 'price', 'promotion', 'chunk', 'embedding'],
        'chunk': ['short_name', 'category'],
        'types':["принтер", "модуль", "терминал", "лицензия", "ккт", "аккумулятор", "ксо", "весы", "ключ", "рычаг", "ограничитель",
                "уплотнитель", "механизм", "разделитель", "крэдл", "ритейл", "бутик", "тумба", "полка", "держатель", "разъем",
                "касс", "pos", "ридер", "ящик", "клавиатура", "дисплей", "сканер", "по", "крышка", "кабель", "блок", "антенна",
                "камера", "ножка", "ручка", "динамик", "frontol", "клеверенс", "optima", "jazz", "чехол", "бампер", "ремешок",
                "панель", "плата", "шестеренка", "датчик", "пружина", "кнопка", "корпус", "диск", "ось", "датчик", "фиксатор",
                "sigma", "двигатель", "шлейф", "рамка", "комплект", "монитор", "компьютер", "selfie", "макс", "планшет", "вставка", "стекло"],
        'excel_column_map': {
            "Код": "article",
            "Товар": "short_name",
            "Акция": "promotion",
            "Розничная цена": "rrc_price",
            "Золото": "price"
        }
    }
}