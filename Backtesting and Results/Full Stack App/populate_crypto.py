import sqlite3

connection = sqlite3.connect('app.db')
cursor = connection.cursor()

Cryptos = [
    ['BTCUSDT', 'Bitcoin', 'TetherUS']]

for Crypto in Cryptos:
    cursor.execute("INSERT INTO crypto (symbol, name, name2) VALUES (?, ?, ?)", (Crypto[0], Crypto[1], Crypto[2]))
    print("Added record for", Crypto[1])
connection.commit()