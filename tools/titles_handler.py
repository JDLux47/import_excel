import pandas as pd


# Находим строку подзаголовок (где заполнено только одно поле)
def detect_category_rows(df):
    mask = df.apply(lambda row: (row.notnull() & (row.astype(str).str.strip() != '')).sum() == 1, axis=1)
    cat_series = df[mask].bfill(axis=1).iloc[:, 0]
    series = pd.Series(index=df.index, dtype='object')
    series.loc[cat_series.index] = cat_series.values
    return series


# Добавляем столбец category с последним встреченным подзаголовком и удаляем подзаголовок из датафрейма
def fill_category_column(df):
    cat_series = detect_category_rows(df)
    cat_filled = cat_series.fillna(method='ffill')
    df['category'] = cat_filled
    df = df[cat_series.isnull()]
    return df