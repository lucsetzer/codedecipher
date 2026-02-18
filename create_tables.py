import sqlite3
conn = sqlite3.connect('bank.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS magic_links (
        token TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        created TIMESTAMP NOT NULL,
        used BOOLEAN DEFAULT 0
    )
''')
conn.commit()
conn.close()
print("✅ Created magic_links table in bank.db")
