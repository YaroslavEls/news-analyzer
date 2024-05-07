create_table_sources = '''CREATE TABLE IF NOT EXISTS sources
                      (id INTEGER PRIMARY KEY,
                      name TEXT)'''

create_table_articles = '''CREATE TABLE IF NOT EXISTS articles
                        (id INTEGER PRIMARY KEY,
                        link TEXT,
                        title TEXT,
                        text TEXT,
                        date TEXT,
                        source_id INTEGER,
                        FOREIGN KEY(source_id) REFERENCES sources(id))'''

select_from_sources = "SELECT id FROM sources WHERE name = ?"

insert_in_sources = "INSERT INTO sources (name) VALUES (?)"

insert_in_articles = "INSERT INTO articles (link, title, text, date, source_id) VALUES (?, ?, ?, ?, ?)"
