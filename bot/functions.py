from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


def get_resources(cursor):
    cursor.execute('select * from sources')
    data = cursor.fetchall()

    i = 1
    res = ''
    for _, name in data:
        res += f'{i}. `{name}`\n'
        i += 1
    return res

def check_if_true(cursor, link):
    cursor.execute('select label from articles where link = ?', (link,))
    row = cursor.fetchone()

    data = int(round(float(row[0]), 2) * 100)
    res = f'`The probability of fakes in this article is {100 - data}%`'
    return res

def _cluster_analysis(data):
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

def _get_data_for_output(df, col_name_1, col_name_2):
    list1 = list(df[col_name_1].value_counts().index)
    counts = list(df[col_name_1].value_counts())
    fake_counts_values = [len(df[(df[col_name_1] == item) & (df['label'] < 0.5)]) for item in list1]

    df_sns = pd.DataFrame({
        col_name_2: list1,
        'total count': counts,
        'fakes count': fake_counts_values
    })
    df_long = df_sns.melt(id_vars=col_name_2, var_name='type', value_name='count')

    return df_sns, df_long

def _save_plot(x, df, title, xlabel, filename):
    plt.figure(figsize=(6, 4))
    sns.barplot(x=x, y='count', hue='type', data=df, palette=['#87cefa', '#ffc87c'])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('Articles count')
    plt.savefig(f'./data/{filename}.png')

def _format_output(df, heading, template, args):
    res = f'{heading}\n'

    for _, row in df.iterrows():
        f_total = "{:,}".format(row['total count'])
        f_fakes = "{:,}".format(row['fakes count'])

        if len(args) == 1:
            tmp = template.format(row[args[0]], f_total, f_fakes)
        elif len(args) == 2:
            tmp = template.format(row[args[0]], f_total, f_fakes, row[args[1]])
        
        res += tmp

    return res

def analyze_period(cursor, start, end):
    date_obj = datetime.strptime(start, '%d.%m.%Y')
    start_date = date_obj.strftime('%Y-%m-%d 00:00:00')
    date_obj = datetime.strptime(end, '%d.%m.%Y')
    end_date = date_obj.strftime('%Y-%m-%d 00:00:00')

    query = "SELECT clean_text, label, source_id FROM articles WHERE date BETWEEN ? AND ?"
    cursor.execute(query, (start_date, end_date))
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['clean_text', 'label', 'source_id'])

    # Cluster analysis for topic identification
    kmeans, top_keywords = _cluster_analysis(df['clean_text'])
    df['kmean_label'] = kmeans.labels_

    # Getting data to use in output and save the plot .png
    df_sns, df_long = _get_data_for_output(df, 'kmean_label', 'topic')
    df_long['topic'] += 1
    _save_plot('topic', df_long, 'Articles by topics', 'Topics', 'plot1')
    
    # Formatting the output
    df_a = df_sns.sort_values(by='topic')
    df_a['topic'] += 1
    words = []
    for i in top_keywords:
        words.append(', '.join(i))
    df_a['keywords'] = words

    template1 = (
        "> Topic {}\n"
        "  Articles count: {}\n"
        "  Articles likely to contain fakes: {}\n"
        "  Keywords: {}\n"
    )
    res1 = _format_output(df_a, 'Identified topics', template1, ['topic', 'keywords'])

    # Getting data to use in output and save the plot .png
    df_sns, df_long = _get_data_for_output(df, 'source_id', 'source')
    _save_plot('source', df_long, 'Articles by sources', 'Sources', 'plot2')

    # Formatting the output
    df_a = df_sns.sort_values(by='source')

    template2 = (
        "> Source {} - <name>\n"
        "  Articles count: {}\n"
        "  Articles likely to contain fakes: {}\n"
    )
    res2 = _format_output(df_a, 'Sources', template2, ['source'])

    # Formatting the final output
    total_len = "{:,}".format(len(df))
    fakes_len = "{:,}".format(len(df[df['label'] < 0.5]))
    final_result = (
        f"```\n"
        f"Details\n"
        f"> Total articles analyzed: {total_len}\n"
        f"> Articles likely to contain fakes detected: {fakes_len}\n"
        f"> Period of time: {start} - {end}\n"
        f"> Sources used: {len(df['source_id'].value_counts())}\n\n"
    )
    final_result += f'{res1}\n{res2}\nPlots are attached\n```'
    
    return final_result
