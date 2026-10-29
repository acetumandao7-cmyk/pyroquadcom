import sqlite3

conn = sqlite3.connect("temperature.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM temperature_readings")

rows = cursor.fetchall()

print("DATABASE CONTENTS")
print("=" * 60)

print("Rows found:", len(rows))

for row in rows:
    print(row)

print("=" * 60)

conn.close()