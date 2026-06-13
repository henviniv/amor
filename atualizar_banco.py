import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS fotos")

cursor.execute("""
CREATE TABLE fotos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Tabela fotos atualizada!")