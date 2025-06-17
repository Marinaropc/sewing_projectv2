import sqlite3
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "patterns.db")

def save_upload_to_db(
    filename, file_type, pattern_type, download_filename,
    bust, waist, hips, torso_height, original_size,
    scale_x, scale_y, resize_response, instructions
):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Insert uploads
    cursor.execute("""
        INSERT INTO uploads (filename, file_type, pattern_type, download_filename)
        VALUES (?, ?, ?, ?)
    """, (filename, file_type, pattern_type, download_filename))
    upload_id = cursor.lastrowid

    # Insert measurements
    cursor.execute("""
        INSERT INTO measurements (upload_id, bust, waist, hips, torso_height, original_size)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (upload_id, bust, waist, hips, torso_height, original_size))

    # Insert scaling
    cursor.execute("""
        INSERT INTO scaling (upload_id, scale_x, scale_y, source)
        VALUES (?, ?, ?, ?)
    """, (upload_id, scale_x, scale_y, "ai"))

    # AI responses
    cursor.execute("""
        INSERT INTO ai_responses (upload_id, type, content)
        VALUES (?, ?, ?)
    """, (upload_id, "resize", resize_response))
    cursor.execute("""
        INSERT INTO ai_responses (upload_id, type, content)
        VALUES (?, ?, ?)
    """, (upload_id, "instructions", instructions))

    connection.commit()
    connection.close()
    return upload_id