import os
import sqlite3
from dotenv import load_dotenv
load_dotenv()


class DatabaseHandler:
    def __init__(self):
        self.conn = sqlite3.connect(os.getenv('DB_FILE'), 
                                    check_same_thread=False)
        self.cursor = self.conn.cursor()

    def disconnect(self):
        self.cursor.close()
        self.conn.close()

    def write_from_df(self, df, col):
        df.to_sql(col, self.conn, if_exists='append', index=False)
        self.conn.commit()

    def create_table_sources(self):
        query = '''
                CREATE TABLE IF NOT EXISTS sources
                (id INTEGER PRIMARY KEY,
                name TEXT)
                '''
        self.cursor.execute(query)
        self.conn.commit()

    def create_table_articles(self):
        query = '''
                CREATE TABLE IF NOT EXISTS articles
                (id INTEGER PRIMARY KEY,
                link TEXT,
                title TEXT,
                text TEXT,
                date TEXT,
                source_id INTEGER,
                clean_text TEXT,
                clean_title TEXT,
                label FLOAT,
                FOREIGN KEY(source_id) REFERENCES sources(id))
                '''
        self.cursor.execute(query)
        self.conn.commit()

    def create_table_preds(self):
        query = '''
                CREATE TABLE IF NOT EXISTS preds
                (id INTEGER PRIMARY KEY,
                clean_text TEXT,
                label FLOAT,
                article_id INTEGER,
                FOREIGN KEY(article_id) REFERENCES articles(id))
                '''
        self.cursor.execute(query)
        self.conn.commit()

    def get_source_id(self, name):
        query = 'SELECT id FROM sources WHERE name = ?'
        self.cursor.execute(query, (name,))
        return self.cursor.fetchone()

    def create_source(self, name):
        query = 'INSERT INTO sources (name) VALUES (?)'
        self.cursor.execute(query, (name,))
        self.conn.commit()
        return self.cursor.lastrowid

    def create_article(self, values):
        query = '''
                INSERT INTO articles 
                (link, title, text, date, source_id) 
                VALUES 
                (?, ?, ?, ?, ?)
                '''
        self.cursor.execute(query, values)
        self.conn.commit()

    def get_articles_between(self, date1, date2):
        query = '''
                SELECT id, title, text 
                FROM articles 
                WHERE date BETWEEN ? AND ?
                '''
        self.cursor.execute(query, (date1, date2))
        return self.cursor.fetchall()
    
    def get_sources(self):
        query = 'SELECT * FROM sources'
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_source(self, id):
        query = '''
                SELECT articles.date, preds.label 
                FROM articles
                JOIN preds ON articles.id = preds.article_id
                WHERE articles.source_id = ?
                '''
        self.cursor.execute(query, (id,))
        return self.cursor.fetchall()
    
    def get_source_name(self, id):
        query = 'SELECT name FROM sources WHERE id = ?'
        self.cursor.execute(query, (id,))
        return self.cursor.fetchone()[0]
    
    def check_source(self, id):
        query = '''
                SELECT EXISTS (
                    SELECT 1 
                    FROM sources
                    WHERE id = ?
                )
                '''
        self.cursor.execute(query, (id,))
        return bool(self.cursor.fetchone()[0])
    
    def get_article_info(self, link):
        query = '''
                SELECT 
                articles.title, articles.date, articles.text, preds.label
                FROM articles
                JOIN preds ON articles.id = preds.article_id
                WHERE articles.link = ?
                '''
        self.cursor.execute(query, (link,))
        return self.cursor.fetchone()
    
    def get_articles_preds(self, date1, date2):
        query = '''
                SELECT preds.clean_text, preds.label, articles.source_id
                FROM articles
                JOIN preds ON articles.id = preds.article_id
                WHERE articles.date BETWEEN ? AND ?
                '''
        self.cursor.execute(query, (date1, date2))
        return self.cursor.fetchall()
    
    def get_articles_preds_ext(self, date1, date2):
        query = '''
                SELECT 
                preds.clean_text, preds.label, articles.title, articles.link
                FROM articles
                JOIN preds ON articles.id = preds.article_id
                WHERE articles.date BETWEEN ? AND ?
                '''
        self.cursor.execute(query, (date1, date2))
        return self.cursor.fetchall()
