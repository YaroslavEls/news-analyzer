import pandas as pd
from datetime import datetime
from interface.commands_error import UserInputError
from database.db_handler import DatabaseHandler
import helpers.base_helpers as b_hlp
import helpers.analysis_helpers as a_hlp


def logging(func):
    def wrapper(*args, **kwargs):
        orange = '\033[38;5;208m{}\033[0m'
        blue = '\033[1m\033[38;5;39m{}\033[0m'
        violet = '\033[1m\033[38;5;135m{}\033[0m'
        purple = '\033[38;5;135m{}\033[0m'

        logs = (
            orange.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            + blue.format(' Command:')
            + f' /{func.__name__}'.ljust(15)
            + violet.format(' Args:')
        )
        for name, value in kwargs.items():
            if name in ['link', 'topic'] and len(value) > 35:
                value = value[:35 - 3] + '...'
            logs += (
                purple.format(f' {name}->')
                + value
            )
        print(logs)

        result = func(*args, **kwargs)
        return result
    return wrapper

def validation(func):
    def wrapper(*args, **kwargs):
        if 'resource_id' in kwargs:
            db = DatabaseHandler()
            is_valid = db.check_source(int(kwargs['resource_id']))
            db.disconnect()
            if not is_valid:
                raise UserInputError(105)
        if 'link' in kwargs:
            pattern = r'\b(?:https?://|www\.)\S+\b'
            if not b_hlp.check_pattern(pattern, kwargs['link']):
                raise UserInputError(101)
        if 'start' in kwargs and 'end' in kwargs:
            try:
                start, end = b_hlp.trans_dates(kwargs['start'], kwargs['end'])
            except ValueError:
                raise UserInputError(102)
            if start > end:
                raise UserInputError(103) 
        if 'topic' in kwargs:
            pattern = r'[а-яА-Яa-zA-Z]'
            if not b_hlp.check_pattern(pattern, kwargs['topic']):
                raise UserInputError(104)
            
        result = func(*args, **kwargs)
        return result
    return wrapper


def _output_resources(data):
    template = '{} {}\n'
    res = '```\nid name\n'
    for id, name in data:
        if len(str(id)) == 1:
            id = str(id).ljust(2)
        res += template.format(id, name)
    res += '\n```'
    return res

@validation
@logging
def resources(db):
    data = db.get_sources()
    return _output_resources(data)

def _output_resource_info(args):
    template = (
        '```\n'
        'Deatils:\n'
        '> Resource name: {}\n'
        '> Resource id: {}\n'
        '> Total articles from this source: {}\n'
        '> Articles likely to contain fakes: {}\n'
        '\n'
        'Activity in the last week:\n'
        '> Total articles: {}\n'
        '> Articles likely to contain fakes: {}\n'
        '\n'
        'Activity in the last month:\n'
        '> Total articles: {}\n'
        '> Articles likely to contain fakes: {}\n'
        '\n'
        'Activity chart for the last 6 months is attached\n'
        '```'
    )
    return template.format(*args)

@validation
@logging
def resource_info(db, id):
    data = db.get_source(id)
    df = pd.DataFrame(data, columns=['date', 'label'])
    df['new_date'] = pd.to_datetime(df['date'])
    current = pd.Timestamp.now()

    # Setting up the plot
    start = current - pd.DateOffset(months=6)
    df_all = df[(df['new_date'] >= start) & (df['new_date'] <= current)]
    df_fake = df_all[df_all['label'] < 0.5]

    vc_all = df_all['new_date'].dt.to_period('M').value_counts()
    vc_fake = df_fake['new_date'].dt.to_period('M').value_counts()

    df_m = pd.DataFrame({
        'month': list(vc_all.index),
        'total count': list(vc_all),
        'fake count': list(vc_fake)
    })
    df_m = df_m.sort_values(by='month')
    df_plot = df_m.melt(id_vars='month', var_name='type', value_name='count')

    plot = a_hlp.plot('month', df_plot, 'Activity for last 6 months', 'Months')

    # Setting up result
    args = [db.get_source_name(id), id, len(df), len(df[df['label'] < 0.5])]
    for offset in [pd.DateOffset(weeks=1), pd.DateOffset(months=1)]:
        start = current - offset
        df_all = df[(df['new_date'] >= start) & (df['new_date'] <= current)]
        args.append(len(df_all))
        args.append(len(df_all[df_all['label'] < 0.5]))

    return _output_resource_info(args), plot

def _output_is_true(args):
    template = (
        '```\n'
        '> Title: {}\n'
        '> Link: {}\n'
        '> Publication date: {}\n'
        '> Leading text: {}\n'
        '\n'
        'The probability of fakes in this article: {}%\n'
        '```'
    )
    return template.format(*args)

@validation
@logging
def is_true(db, link):
    data = db.get_article_info(link)

    title = b_hlp.preprocess_output(data[0])
    date = data[1][:10]
    lead = b_hlp.preprocess_output(data[2])[:300] + '...'
    label = 100 - int(round(float(data[3]), 2) * 100)

    return _output_is_true([title, link, date, lead, label])

def _output_analyze(args, topic_df, source_df):
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

    res += '\nSources with the most articles\n'
    for _, row in source_df.iterrows():
        total = "{:,}".format(row['total count'])
        fakes = "{:,}".format(row['fakes count'])
        res += template3.format(row['source'], row['name'], total, fakes)

    res += '\nSome charts are attached\n```'
    return res

@validation
@logging
def analyze(db, start, end):
    start_date, end_date = b_hlp.trans_dates(start, end)
    data = db.get_articles_preds(start_date, end_date)
    df = pd.DataFrame(data, columns=['clean_text', 'label', 'source_id'])

    # Cluster analysis for topic identification
    kmeans, top_keywords = a_hlp.cluster_analysis(df['clean_text'])
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
    plot1 = a_hlp.plot('topic', df_plot, 'Articles by topics', 'Topics')
    
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
    plot2 = a_hlp.plot('source', df_plot, 'Articles by sources', 'Sources')

    df_source = df_source.sort_values(by='source')
    sources_data = dict(db.get_sources())
    df_source['name'] = df_source['source'].map(sources_data)
    df_source = df_source.nlargest(5, 'total count')

    # Formatting the output
    args = [
        "{:,}".format(len(df)),
        "{:,}".format(len(df[df['label'] < 0.5])),
        start,
        end,
        len(df['source_id'].value_counts())
    ]
    wc = a_hlp.word_cloud(df['clean_text'])
    return _output_analyze(args, df_topic, df_source), (plot1, plot2, wc)

def _output_find(args, df):
    template1 = (
        '```\n'
        'Details\n'
        '> Topic: {}\n'
        '> Total articles analyzed: {}\n'
        '> Articles relevant to the topic found: {}\n'
        '> Articles likely to contain fakes on topic: {}\n'
        '> Period of time: {} - {}\n'
    )
    template2 = (
        '> Article {}\n'
        '  Title: {}\n'
        '  Link: {}\n'
        '  The probability of fakes in this article: {}%\n'
    )

    res = template1.format(*args)

    if len(df) == 0:
        return res + '```'

    res += '\nArticles most relevant to the topic\n'
    for i, row in df.head(5).iterrows():
        title = b_hlp.preprocess_output(row['title'])
        label = str(100 - int(round(float(row['label']), 2) * 100)).zfill(2)
        res += template2.format(i+1, title, row['link'], label)

    return res + '```'

@validation
@logging
def find(db, topic, start, end):
    start_date, end_date = b_hlp.trans_dates(start, end)
    data = db.get_articles_preds_ext(start_date, end_date)
    df = pd.DataFrame(data, columns=['clean_text', 'label', 'title', 'link'])

    # Calculate similarities
    topic = b_hlp.preprocessor(topic)
    scores = a_hlp.similarity(topic, list(df['clean_text']))
    df['score'] = scores
    df = df.sort_values(by='score', ascending=False)
    df_relevant = df[df['score'] > 0.1]
    
    # Formatting the output
    args = [
        topic,
        "{:,}".format(len(df)),
        "{:,}".format(len(df_relevant)),
        "{:,}".format(len(df_relevant[df_relevant['label'] < 0.5])),
        start,
        end
    ]
    return _output_find(args, df_relevant)
