from threading import Thread
import pandas as pd
from database.db_handler import DatabaseHandler
import parsers as ps
from pipelines import pipeline


start = '01.05.2023'
end = '05.05.2023'
db = DatabaseHandler()

db.create_table_sources()
db.create_table_articles()

threads = [
    Thread(target=pipeline, 
           args=(ps.UkrPravdaParser(), start, end, db)),
    Thread(target=pipeline, 
           args=(ps.UnianParser(), start, end, db)),
    Thread(target=pipeline, 
           args=(ps.TsnParser(), start, end, db)),
    Thread(target=pipeline, 
           args=(ps.RbcParser(), start, end, db)),
    Thread(target=pipeline, 
           args=(ps.SuspilneParser, start, end, db)),
    Thread(target=pipeline, 
           args=(ps.TelegramParser('babel', '31744'), start, end, db)),
    Thread(target=pipeline, 
           args=(ps.TelegramParser('UkraineNow', '32420'), start, end, db)),
    Thread(target=pipeline, 
           args=(ps.TelegramParser('spravdi', '28559'), start, end, db)),
    Thread(target=pipeline, 
           args=(ps.TelegramParser('gruntmedia', '31226'), start, end, db)),
    Thread(target=pipeline, 
           args=(ps.TelegramParser('informnapalm', '16817'), start, end, db)),
]

for t in threads: 
    t.start()

for t in threads: 
    t.join()
