import pandas as pd

file_path = 'Клеверенс_Склад_15_Прайс_лист_28_03_2025_РФ_4.xlsx'
sheet_name = 'Маркировки'

df = pd.read_excel(file_path, sheet_name=sheet_name)

first_col = df.columns[0]  # первый столбец
categories = ['вещевой', 'продуктовый']
col_map = {col.lower(): col for col in df.columns}
cat_cols = [col_map.get(cat) for cat in categories]

result = {}
for _, row in df.iterrows():
    cats = []
    for cat, col in zip(categories, cat_cols):
        if col and str(row[col]).strip().lower() == 'да':
            cats.append(cat)
    if cats:
        result[str(row[first_col]).strip()] = cats

# Записываем как Python-словарь
with open('markings_dict.py', 'w', encoding='utf-8') as f:
    f.write('match_dict = {\n')
    for key, value in result.items():
        key_str = repr(key)
        value_str = '[' + ', '.join(f'"{v}"' for v in value) + ']'
        f.write(f'  {key_str}: {value_str},\n')
    f.write('}\n')
