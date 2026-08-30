import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "depression.db")

print("Using Database:", DB_PATH)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Create history table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    analysis_type TEXT,
    score REAL,
    level TEXT,
    date TEXT
)
""")

# Add patient information columns to existing database
columns = [
    ("patient_name", "TEXT"),
    ("patient_age", "INTEGER"),
    ("patient_gender", "TEXT"),
    ("patient_occupation", "TEXT"),
    ("patient_symptoms", "TEXT"),
    ("patient_duration", "TEXT"),
    ("patient_started", "TEXT")
]

for column_name, column_type in columns:

    cursor.execute(
        "PRAGMA table_info(history)"
    )

    existing_columns = [
        row[1] for row in cursor.fetchall()
    ]

    if column_name not in existing_columns:

        cursor.execute(
            f"ALTER TABLE history ADD COLUMN {column_name} {column_type}"
        )

        print(f"Added column: {column_name}")

conn.commit()