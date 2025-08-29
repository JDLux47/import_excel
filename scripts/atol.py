import os
from configs.columns import COLUMNS
from configs.table_config import TABLE_CONFIGS
from init_objects import engine
from tools.parameters import add_parameters_column
from tools.titles_handler import fill_category_column
from tools.tools import create_table_from_config, read_excel_file, rename_columns, strip_selected_columns, \
    filter_rows_with_price, select_final_columns, add_chunk_column, add_embedding, insert_into_db

# Основная логика добавления прайса атол
def import_excel_atol(excel_path):
    filename = os.path.basename(excel_path)
    table_config = TABLE_CONFIGS.get(filename)

    table_name = table_config['table_name']
    columns = table_config['columns']
    chunk_fields = table_config['chunk']
    sheet_name = table_config.get('sheet_name')
    col_map = table_config['excel_column_map']
    header_num = table_config['header']
    types = table_config.get('types')

    # Добавим новую колонку заранее, если ее нет
    if 'category' not in columns:
        columns = columns + ['category']
    if types and "parameters" not in columns:
        columns = columns + ["parameters"]

    table = create_table_from_config(table_name, columns)
    table.drop(engine, checkfirst=True)
    table.create(engine, checkfirst=True)

    for sheet in sheet_name:
        df = read_excel_file(excel_path, sheet, COLUMNS, header_num)
        # 1. Добавляем колонку category из подзаголовков, удаляя сами подзаголовки
        df = fill_category_column(df)
        # 2. Приводим к нужным столбцам, далее все шаги как раньше
        df = rename_columns(df, col_map)
        df = strip_selected_columns(df, col_map.values())
        df = filter_rows_with_price(df)
        df = select_final_columns(df, columns)
        df = add_chunk_column(df, chunk_fields)
        df = add_embedding(df)
        if types:
            df = add_parameters_column(df, types)
        insert_into_db(table, df, columns)