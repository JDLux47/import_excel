import os
from configs.columns import COLUMNS
from configs.table_config import TABLE_CONFIGS
from init_objects import engine
from tools.tools import create_table_from_config, read_excel_file, rename_columns, strip_selected_columns, \
    filter_rows_with_price, select_final_columns, add_chunk_column, add_embedding, insert_into_db

# Основная логика добавления прайса клеверенс
def import_excel_cleverens(excel_path):
    filename = os.path.basename(excel_path)
    table_config = TABLE_CONFIGS.get(filename)

    table_name = table_config['table_name']
    columns = table_config['columns']
    chunk_fields = table_config['chunk']
    sheet_name = table_config.get('sheet_name')
    col_map = table_config['excel_column_map']
    header_num = table_config['header']

    table = create_table_from_config(table_name, columns)
    table.drop(engine, checkfirst=True)
    table.create(engine, checkfirst=True)

    for sheet in sheet_name:
        df = read_excel_file(excel_path, sheet, COLUMNS, header_num)
        df = rename_columns(df, col_map)
        df = strip_selected_columns(df, col_map.values())
        df = filter_rows_with_price(df)
        df = select_final_columns(df, columns)
        df = add_chunk_column(df, chunk_fields)
        df = add_embedding(df)
        insert_into_db(table, df, columns)