import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fotos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arquivo TEXT NOT NULL
)
""")

# Usuários

cursor.execute("""
INSERT OR IGNORE INTO usuarios
(username,password)
VALUES
('vinicius','amoataiana')
""")

cursor.execute("""
INSERT OR IGNORE INTO usuarios
(username,password)
VALUES
('taiana','amovinicius')
""")

conn.commit()
conn.close()

print("Banco criado com sucesso!")