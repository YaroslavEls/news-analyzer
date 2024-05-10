import re
import pandas as pd

import helpers as hlp


def _output4_get_resources(data):
    template = '{}. {}\n'
    res = '```\n'
    for id, name in data:
        res += template.format(id, name)
    res += '\n```'
    return res

def get_resources(db):
    data = db.get_sources()
    return _output4_get_resources(data)

def _output4_check_if_true(num):
    return f'```The probability of fakes in this article is {num}%```'

def check_if_true(db, link):
    label = db.get_article_lable(link)
    label = 100 - int(round(float(label[0]), 2) * 100)
    return _output4_check_if_true(label)

def _output4_analyze_period(args, topic_df, source_df):
    template1 = (
        '```\n'
        'Details\n'
        '> Total articles analyzed: {}\n'
        '> Articles likely to contain fakes detected: {}\n'
        '> Period of time: {} - {}\n'
        '> Sources used: {}\n'
    )
    template2 = (
        '> Topic {}\n'
        '  Articles count: {}\n'
        '  Articles likely to contain fakes: {}\n'
        '  Keywords: {}\n'
    )
    template3 = (
        '> Source {} - {}\n'
        '  Articles count: {}\n'
        '  Articles likely to contain fakes: {}\n'
    )
    
    res = template1.format(*args)

    res += '\nIdentified topics\n'
    for _, row in topic_df.iterrows():
        total = "{:,}".format(row['total count'])
        fakes = "{:,}".format(row['fakes count'])
        res += template2.format(row['topic'], total, fakes, row['keywords'])

    res += '\nSources\n'
    for _, row in source_df.iterrows():
        total = "{:,}".format(row['total count'])
        fakes = "{:,}".format(row['fakes count'])
        res += template3.format(row['source'], row['name'], total, fakes)

    res += '\nPlots are attached\n```'
    return res

def analyze_period(db, start, end):
    # Getting data from the database
    start_date, end_date = hlp.trans_dates(start, end)
    data = db.get_articles_preds(start_date, end_date)
    df = pd.DataFrame(data, columns=['clean_text', 'label', 'source_id'])

    # Cluster analysis for topic identification
    kmeans, top_keywords = hlp.cluster_analysis(df['clean_text'])
    df['kmean_label'] = kmeans.labels_

    # Preparing data about topics
    vc = df['kmean_label'].value_counts()
    df_topic = pd.DataFrame({
        'topic': [x + 1 for x in list(vc.index)],
        'total count': list(vc),
        'fakes count': [
            len(df[(df['kmean_label'] == item) & (df['label'] < 0.5)]) \
                for item in list(vc.index)
        ]
    })

    df_plot = df_topic.melt(id_vars='topic', 
                            var_name='type', 
                            value_name='count')
    plot1 = hlp.plot('topic', df_plot, 'Articles by topics', 'Topics')
    
    df_topic = df_topic.sort_values(by='topic')
    df_topic['keywords'] = [', '.join(word) for word in top_keywords]

    # Preparing data about sources
    vc = df['source_id'].value_counts()
    df_source = pd.DataFrame({
        'source': list(vc.index),
        'total count': list(vc),
        'fakes count': [
            len(df[(df['source_id'] == item) & (df['label'] < 0.5)]) \
                for item in list(vc.index)
        ]
    })

    df_plot = df_source.melt(id_vars='source', 
                            var_name='type', 
                            value_name='count')
    plot2 = hlp.plot('source', df_plot, 'Articles by sources', 'Sources')

    df_source = df_source.sort_values(by='source')
    sources_data = dict(db.get_sources())
    df_source['name'] = df_source['source'].map(sources_data)

    # Formatting the output
    args = [
        "{:,}".format(len(df)),
        "{:,}".format(len(df[df['label'] < 0.5])),
        start,
        end,
        len(df['source_id'].value_counts())
    ]
    return _output4_analyze_period(args, df_topic, df_source), (plot1, plot2)

def _output4_find_n_analyze(args, df):
    template1 = (
        '```\n'
        'Details\n'
        'Topic: {}\n'
        '> Total articles analyzed: {}\n'
        '> Articles likely to contain fakes detected: {}\n'
        '> Period of time: {} - {}\n'
    )
    template2 = (
        '> Article {}\n'
        '  Title: {}\n'
        '  Link: {}\n'
        '  The probability of fakes in this article: {}%\n'
    )

    res = template1.format(*args)

    res += '\nArticles most relevant to the topic\n'
    for i, row in df.head(5).iterrows():
        title = row['title']
        title = re.sub(r'\b\d{2}:\d{2}\b', '', title)
        title = re.sub('\n', '', title)
        title = ' '.join(title.strip().split())
        label = str(100 - int(round(float(row['label']), 2) * 100)).zfill(2)
        res += template2.format(i+1, title, row['link'], label)

    res += '```'
    return res

# TODO: add string 'articles relevant to the topic count' to the output details
def find_n_analyze(db, topic, start, end):
    # Getting data from the database
    start_date, end_date = hlp.trans_dates(start, end)
    data = db.get_articles_preds_ext(start_date, end_date)
    df = pd.DataFrame(data, columns=['clean_text', 'label', 'title', 'link'])

    # Calculate similarities
    topic = hlp.preprocessor(topic)
    scores = hlp.similarity(topic, list(df['clean_text']))
    df['score'] = scores
    df = df.sort_values(by='score', ascending=False)
    
    # Formatting the output
    args = [
        topic,
        "{:,}".format(len(df)),
        "{:,}".format(len(df[df['label'] < 0.5])),
        start,
        end
    ]
    return _output4_find_n_analyze(args, df)
