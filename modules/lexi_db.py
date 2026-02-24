import sqlite3
from datetime import datetime, timedelta

def get_connection():
    return sqlite3.connect('lexi_wordbank.db')

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS words 
                 (word TEXT PRIMARY KEY, 
                  definition TEXT, 
                  phonetic TEXT, 
                  category TEXT,
                  date_added DATE DEFAULT CURRENT_DATE, 
                  next_review DATE)''')
    conn.commit()
    conn.close()

def save_word(word, definition, phonetic, category):
    conn = get_connection()
    c = conn.cursor()
    next_review = (datetime.now() + timedelta(days=3)).date()
    try:
        c.execute("INSERT INTO words (word, definition, phonetic, category, next_review) VALUES (?, ?, ?, ?, ?)", 
                  (word, definition, phonetic, category, next_review))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()