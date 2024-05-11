import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import random
from wordcloud import WordCloud
from dotenv import load_dotenv
load_dotenv()


def cluster_analysis(data):
    vectorizer = TfidfVectorizer(max_features=1000)
    matrix = vectorizer.fit_transform(data)
    kmeans = KMeans(n_clusters=5, n_init=10)
    kmeans.fit(matrix)

    feature_names = vectorizer.get_feature_names_out()
    top_keywords = []
    for cluster_center in kmeans.cluster_centers_:
        top_keyword_idxs = cluster_center.argsort()[-5:][::-1]
        top_keywords.append([feature_names[idx] for idx in top_keyword_idxs])

    return kmeans, top_keywords

def similarity(string, data):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([string] + data)
    
    return cosine_similarity(vectors[0], vectors[1:])[0]

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

def word_cloud(data):
    num = random.randint(1, 10000000)
    path = f'{os.getenv("DATA_PATH")}/{str(num)}.png'

    wc = WordCloud(background_color="black", 
                max_words=100,
                max_font_size=256,
                random_state=0, 
                width=1000, 
                height=1000)
    wc.generate(' '.join(data))
    plt.figure()
    plt.axis('off')
    plt.imshow(wc, interpolation="bilinear")
    plt.savefig(path)

    return path
