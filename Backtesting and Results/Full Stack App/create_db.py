import sqlite3
connection = sqlite3.connect('app.db')
cursor = connection.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS crypto (
        id INTEGER PRIMARY KEY, 
        symbol TEXT NOT NULL UNIQUE, 
        name TEXT NOT NULL,
        name2 TEXT NOT NULL
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS crypto_price (
        id INTEGER PRIMARY KEY, 
        crypto_id INTEGER,
        opentime NOT NULL,
        open NOT NULL, 
        high NOT NULL, 
        low NOT NULL, 
        close NOT NULL,
        volume NOT NULL,
        UNIQUE (crypto_id, opentime, open, high, low, close, volume) ON CONFLICT IGNORE,
        FOREIGN KEY (crypto_id) REFERENCES crypto (id)
    )
""")
connection.commit()