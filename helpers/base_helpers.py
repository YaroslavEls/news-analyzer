from datetime import datetime
import re
import string
import spacy


nlp = spacy.load("uk_core_news_sm")

seqs_to_del = [
    'підписуйтесь канал telegram viber',
    'термінові важливий',
    'терміновий важливий',
    'повідомлення війна росія україна читати канал рбк україна telegram',
    'повідомляти рбк україна ',
    'рбк україна ',
    'читати',
    'підписуватися ukraine now', 
    'babel', 
    'bloomberg',
    'spravdi',
    'informnapalm',
    'підписатись',
    'сайт',
    'нин', 
    'https'
    'telegram', 
    'instagram', 
    'twitter', 
    'facebook', 
    'viber',
    # 'україна', 
    # 'український',
    # 'росія',
    # 'російський',
]

def trans_dates(date1, date2):
    date_obj = datetime.strptime(date1, '%d.%m.%Y')
    date1_trans = date_obj.strftime('%Y-%m-%d 00:00:00')
    date_obj = datetime.strptime(date2, '%d.%m.%Y')
    date2_trans = date_obj.strftime('%Y-%m-%d 00:00:00')
    return date1_trans, date2_trans

def check_pattern(pattern, str):
    return bool(re.search(pattern, str))

def preprocessor(text):
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub("\\W"," ",text) 
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)
    return text

def preprocess_text(text):
    text = preprocessor(text)
    
    doc = nlp(text)
    lemma_tokens = \
        [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    text = ' '.join(lemma_tokens)

    for seq in seqs_to_del:
        text = text.replace(seq, '')
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text

def preprocess_output(text):
    text = re.sub(r'\b\d{2}:\d{2}\b', '', text)
    text = re.sub('\n', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = ' '.join(text.strip().split())
    return text
