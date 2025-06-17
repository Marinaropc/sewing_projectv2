import sqlite3

def init_db():
    """
    Create the database and all tables if they don't already exist.
    Run this once at the start of the project.
    """
    conn = sqlite3.connect("patterns.db")
    cursor = conn.cursor()

    # Main upload info
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        file_type TEXT,
        pattern_type TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        download_filename TEXT
    )
    """)

    # Measurements table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_id INTEGER,
        bust REAL,
        waist REAL,
        hips REAL,
        torso_height REAL,
        original_size TEXT,
        FOREIGN KEY (upload_id) REFERENCES uploads(id)
    )
    """)

    # Scaling info
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scaling (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_id INTEGER,
        scale_x REAL,
        scale_y REAL,
        source TEXT,
        FOREIGN KEY (upload_id) REFERENCES uploads(id)
    )
    """)

    # AI-generated responses
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_id INTEGER,
        type TEXT,
        content TEXT,
        FOREIGN KEY (upload_id) REFERENCES uploads(id)
    )
    """)

    conn.commit()
    conn.close()