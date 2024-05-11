import pandas as pd
import parsers as ps
import helpers.base_helpers as b_hlp
import helpers.load_helpers as l_hlp
from database.db_handler import DatabaseHandler


def parse_many(parser: ps.Parser, start: str, end: str):
    data = parser.run(date1=start, date2=end)
    cols = ['link', 'title', 'text', 'date', 'source_id']
    return pd.DataFrame(data, columns=cols)

def preprocess(df: pd.DataFrame):
    df['clean_text'] = df['text'].apply(b_hlp.preprocess_text)
    df['clean_title'] = df['title'].apply(b_hlp.preprocessor)
    return df

def predict(df: pd.DataFrame):
    model = l_hlp.load_model()
    preds = model.predict_proba(df['clean_title'])
    df['label'] = preds[:,1:]
    return df

def write(df: pd.DataFrame, db: DatabaseHandler):
    db.write_from_df(df, 'articles')
    return df


def pipeline(parser: ps.Parser, start: str, end: str, db: DatabaseHandler):
    df = parse_many(parser, start, end)
    df = preprocess(df)
    df = predict(df)
    write(df, db)
