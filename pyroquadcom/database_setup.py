import sqlite3

DATABASE = "temperature.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS temperature_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature REAL NOT NULL,
    status TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Database created successfully!")
print("Database:", DATABASE)
print("Table: temperature_readings")