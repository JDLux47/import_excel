import re
from natasha import NewsNERTagger, NewsEmbedding, MorphVocab, Segmenter
from init_objects import logger
from configs.synonyms import SYNONYMS_GROUPS

segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
ner_tagger = NewsNERTagger(emb)


# Определяем какие из параметров упоминаются в тексте и добавляем синонимы
def detect_device_types_natasha(text, allowed_types, synonym_map):
    text_lower = text.lower()
    found_synonyms = set()
    for dev_type in allowed_types:
        if not dev_type:
            continue
        dev_type_low = re.escape(dev_type.lower())
        pattern = r'(?<![a-zа-яё]){}(?![a-zа-яё])'.format(dev_type_low)
        if re.search(pattern, text_lower, re.IGNORECASE):
            # Попали в группу синонимов если есть, иначе просто слово
            group = synonym_map.get(dev_type.lower(), {dev_type})
            found_synonyms.update(group)
    return ', '.join(sorted(found_synonyms)) if found_synonyms else ""


# Добавляем колонку с параметрами в датафрейм
def add_parameters_column(df, types):
    logger.info(f"Find types by Natasha from: {types}")

    synonym_map = {}
    for group in SYNONYMS_GROUPS:
        for synonym in group:
            synonym_map[synonym] = group

    df['parameters'] = df['chunk'].apply(
        lambda x: detect_device_types_natasha(str(x) if x is not None else '', types, synonym_map)
    )
    logger.info("Column 'parameters' created.")
    return df