import threading
import pandas as pd

from db_handler import DatabaseHandler
import parsers
import helpers as hlp


# STEP 1: Init db
db = DatabaseHandler()
db.create_table_sources()
db.create_table_articles()
db.create_table_preds()

print('step 1 complete')

# STEP 2: Parse data from web-resources and write to db
start = '01.05.2023'
end = '05.05.2024'

threads = [
    threading.Thread(target=parsers.UkrPravdaParser().run, 
                     args=(start, end)),
    threading.Thread(target=parsers.UnianParser().run, 
                     args=(start, end)),
    threading.Thread(target=parsers.TsnParser().run, 
                     args=(start, end)),
    threading.Thread(target=parsers.RbcParser().run, 
                     args=(start, end)),
    threading.Thread(target=parsers.SuspilneParser().run, 
                     args=(start, end)),
    threading.Thread(target=parsers.TelegramParser('babel', '31744').run,
                     args=(start, end)),
    threading.Thread(target=parsers.TelegramParser('UkraineNow', '32420').run,
                     args=(start, end)),
    threading.Thread(target=parsers.TelegramParser('spravdi', '28559').run,
                     args=(start, end)),
    threading.Thread(target=parsers.TelegramParser('gruntmedia', '31226').run,
                     args=(start, end)),
    threading.Thread(target=parsers.TelegramParser('informnapalm', '16817').run,
                     args=(start, end)),
]

for t in threads: 
    t.start()

for t in threads: 
    t.join()

print('step 2 complete')

# STEP 3: Create dataframe from data that has been just recorded
start_date, end_date = hlp.trans_dates(start, end)
data = db.get_articles_between(start_date, end_date)
df = pd.DataFrame(data, columns=['id', 'title', 'text'])

print('step 3 complete')

# STEP 4: Preprocess the data
df['clean_text'] = df['text'].apply(hlp.preprocess_text)
df['clean_title'] = df['title'].apply(hlp.preprocessor)

print('step 4 complete')

# STEP 5: Process the data and write results to db
model = hlp.load_model()
preds = model.predict_proba(df['clean_title'])
df['label'] = preds[:,1:]

df_sql = pd.DataFrame({
    'clean_text': df['clean_text'], 
    'label': df['label'], 
    'article_id': df['id']
})
db.write_from_df(df_sql, 'preds')

print(df_sql.head())
print('step 5 complete')
