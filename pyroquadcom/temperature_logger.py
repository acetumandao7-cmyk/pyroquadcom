import serial
import sqlite3
from datetime import datetime
import re
import time

PORT = "COM7"
BAUD_RATE = 9600
DATABASE = "temperature.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

try:
    arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)
    print("Connected to Arduino Nano on", PORT)
except serial.SerialException as e:
    print("Could not connect to Arduino.")
    print(e)
    conn.close()
    exit()

time.sleep(2)

print("Continuous temperature logging started.")
print("Press CTRL+C to stop.")
print()

temperature = None
status = None

try:

    while True:

        line = arduino.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if not line:
            continue

        print("Arduino:", line)

        if line.startswith("Temperature:"):

            match = re.search(
                r"Temperature:\s*(-?\d+(?:\.\d+)?)",
                line
            )

            if match:
                temperature = float(match.group(1))

        elif line.startswith("STATUS:"):

            status = line.replace("STATUS:", "").strip()

        if temperature is not None and status is not None:

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            cursor.execute("""
                INSERT INTO temperature_readings
                (timestamp, temperature, status)
                VALUES (?, ?, ?)
            """, (
                timestamp,
                temperature,
                status
            ))

            conn.commit()

            print(
                f"SAVED | {timestamp} | "
                f"{temperature:.2f} C | {status}"
            )

            print()

            temperature = None
            status = None

except KeyboardInterrupt:

    print()
    print("Stopping temperature logger...")

finally:

    arduino.close()
    conn.close()

    print("Arduino connection closed.")
    print("Database connection closed.")
    print("Logger stopped.")