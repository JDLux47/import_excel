import os
import pandas as pd
from configs.columns import COLUMNS
from configs.table_config import TABLE_CONFIGS
from tools.db import insert_into_qdrant
from tools.duplicates_promo_delete import process_duplicates_with_promo
from tools.embedding import add_chunk_column, add_embedding
from tools.parameters import add_parameters_column
from tools.titles_handler import fill_category_column
from tools.tools import read_excel_file, rename_columns, strip_selected_columns, filter_rows_with_price, select_final_columns


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

    dfs = []
    for sheet in sheet_name:
        df = read_excel_file(excel_path, sheet, COLUMNS, header_num)
        df = fill_category_column(df)
        df = rename_columns(df, col_map)
        df = strip_selected_columns(df, col_map.values())
        df = filter_rows_with_price(df)
        df = select_final_columns(df, columns)
        df = add_chunk_column(df, chunk_fields)
        df = add_embedding(df)
        if types:
            df = add_parameters_column(df, types)
        dfs.append(df)

    all_df = pd.concat(dfs, ignore_index=True)
    all_df = process_duplicates_with_promo(all_df)
    insert_into_qdrant(table_name, all_df, columns)