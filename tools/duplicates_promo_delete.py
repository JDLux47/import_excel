import numpy as np
import pandas as pd

# Удаляем дубликаты, которые по акции, устанавливаем флаг is_promo в 1 у товаров по акции
def process_duplicates_with_promo(df):
    df['is_promo'] = 0
    df = df.copy()
    df['promo'] = np.nan

    mask_action = df['category'].str.upper().str.contains("АКЦИЯ", na=False)

    df_action = df[mask_action]
    to_remove = []

    for idx, row in df_action.iterrows():
        code = row['article']
        promo_text = f"{row['category']} (РРЦ: {row['rrc_price']}, Цена: {row['price']})"
        mask_main = (df['article'] == code) & (~mask_action)
        candidates = df[mask_main]
        if not candidates.empty:
            main_idx = candidates.index[0]
            df.at[main_idx, 'promo'] = promo_text
            df.at[main_idx, 'is_promo'] = 1
            to_remove.append(idx)
        else:
            df.at[idx, 'promo'] = promo_text
            df.at[idx, 'is_promo'] = 1

    df = df.drop(index=to_remove)
    df = df.drop_duplicates(subset=['article'], keep='first')
    df = df.reset_index(drop=True)
    return df