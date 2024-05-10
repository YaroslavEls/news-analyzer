import os
from datetime import datetime
import re
import string
import spacy
import joblib
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import random

load_dotenv()

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
    
    'україна', 
    'український',
    'росія',
    'російський',
]

def trans_dates(date1, date2):
    date_obj = datetime.strptime(date1, '%d.%m.%Y')
    date1_trans = date_obj.strftime('%Y-%m-%d 00:00:00')
    date_obj = datetime.strptime(date2, '%d.%m.%Y')
    date2_trans = date_obj.strftime('%Y-%m-%d 00:00:00')
    return date1_trans, date2_trans

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

def load_model():
    return joblib.load(os.getenv('MODEL_FILE'))
    
def cluster_analysis(data):
    vectorizer = TfidfVectorizer(max_features=1000)
    matrix = vectorizer.fit_transform(data)
    kmeans = KMeans(n_clusters=5)
    kmeans.fit(matrix)

    feature_names = vectorizer.get_feature_names_out()
    top_keywords = []
    for cluster_center in kmeans.cluster_centers_:
        top_keyword_idxs = cluster_center.argsort()[-5:][::-1]
        top_keywords.append([feature_names[idx] for idx in top_keyword_idxs])

    return kmeans, top_keywords

def plot(x, df, title, xlabel):
    num = random.randint(1, 10000000)
    path = f'{os.getenv("DATA_PATH")}/{str(num)}.png'

    plt.figure(figsize=(6, 4))
    sns.barplot(x=x, y='count', hue='type', 
                data=df, palette=['#87cefa', '#ffc87c'])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('Articles count')
    plt.savefig(path)
    
    return path

def similarity(string, data):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([string] + data)
    
    return cosine_similarity(vectors[0], vectors[1:])[0]