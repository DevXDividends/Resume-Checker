import sqlite3
from database import DB_NAME

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

try:
    c.execute("ALTER TABLE resumes ADD COLUMN feedback TEXT")
    print("Column added successfully.")
except sqlite3.OperationalError:
    print("Column already exists.")
finally:
    conn.commit()
    conn.close()
