import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

DB_NAME = "resume_system.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Admin table
    c.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    """)

    # Job Description table
    c.execute("""
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        filename TEXT,
        upload_date TEXT
    )
    """)

    # Resume table   ### i have added and extra column here
    c.execute("""   
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_name TEXT,
        jd_id INTEGER,
        resume_text TEXT,
        filename TEXT,
        score REAL,
        verdict TEXT,
        upload_date TEXT,
        FOREIGN KEY(jd_id) REFERENCES job_descriptions(id)
    )
    """)

    conn.commit()
    conn.close()

# Admin helper functions
def add_admin(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        c.execute("INSERT INTO admin (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Admin username already exists.")
    conn.close()

def verify_admin(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM admin WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return check_password_hash(row[0], password)
    return False

# Job Description helper
def add_jd(title, description, filename):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO job_descriptions (title, description, filename, upload_date) VALUES (?, ?, ?, ?)",
              (title, description, filename, upload_date))
    conn.commit()
    conn.close()

def get_all_jds():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, title,description FROM job_descriptions ORDER BY upload_date DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# Resume helper
def add_resume(candidate_name, jd_id, resume_text, filename, score, verdict):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""INSERT INTO resumes 
                 (candidate_name, jd_id, resume_text, filename, score, verdict, upload_date) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (candidate_name, jd_id, resume_text, filename, score, verdict, upload_date))
    conn.commit()
    conn.close()

def get_resumes_for_jd(jd_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT candidate_name, score, verdict, filename FROM resumes WHERE jd_id = ?", (jd_id,))
    rows = c.fetchall()
    conn.close()
    return rows




def get_job_by_id(jd_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, title, description FROM job_descriptions WHERE id = ?", (jd_id,))
    job = c.fetchone()
    conn.close()
    return job  # returns tuple (id, title, description) or None




def delete_job(jd_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM job_descriptions WHERE id=?", (jd_id,))
    conn.commit()
    conn.close()


