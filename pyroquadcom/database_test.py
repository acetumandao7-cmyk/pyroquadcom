import sqlite3

DATABASE = "temperature.db"

temperature = 27.50
status = "NORMAL"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute("""
INSERT INTO temperature_readings (temperature, status)
VALUES (?, ?)
""", (temperature, status))

conn.commit()
conn.close()

print("Test reading saved!")
print(f"Temperature: {temperature:.2f} C")
print(f"Status: {status}")