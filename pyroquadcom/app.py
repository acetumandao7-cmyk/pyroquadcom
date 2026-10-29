from flask import Flask, render_template, jsonify, Response
import sqlite3
import csv
import io
import serial
import threading
from datetime import datetime
import time

app = Flask(__name__)

DATABASE = "temperature.db"

# =========================
# SERIAL SETTINGS
# =========================

SERIAL_PORT = "COM8"
BAUD_RATE = 9600

serial_connection = None
serial_thread = None


# =========================
# DATABASE CONNECTION
# =========================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# DATABASE INITIALIZATION
# =========================

def initialize_database():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperature_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temperature REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# SERIAL CONNECTION
# =========================

def connect_serial():

    global serial_connection

    try:

        serial_connection = serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=1
        )

        print("--------------------------------")
        print("CP2102 SERIAL CONNECTED")
        print("PORT:", SERIAL_PORT)
        print("BAUD RATE:", BAUD_RATE)
        print("--------------------------------")

        # Give Nano time to reset
        time.sleep(2)

        # Clear old serial data
        serial_connection.reset_input_buffer()

        return True

    except Exception as e:

        print("--------------------------------")
        print("CP2102 SERIAL CONNECTION ERROR")
        print(e)
        print("--------------------------------")

        serial_connection = None

        return False


# =========================
# READ SERIAL DATA
# =========================

def serial_reader():

    global serial_connection

    while True:

        try:

            if serial_connection is None:

                if not connect_serial():
                    time.sleep(5)
                    continue

            if serial_connection.in_waiting > 0:

                line = serial_connection.readline().decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                if line:

                    print("SERIAL:", line)

                    # =========================
                    # EXPECTED FORMAT:
                    #
                    # DATA,30.62,WARNING
                    # =========================

                    if line.startswith("DATA,"):

                        parts = line.split(",")

                        if len(parts) == 3:

                            try:

                                temperature = float(parts[1])
                                status = parts[2].strip()

                                timestamp = datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )

                                conn = get_db_connection()
                                cursor = conn.cursor()

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
                                conn.close()

                                print(
                                    f"DATABASE SAVED: "
                                    f"{temperature:.2f} C - {status}"
                                )

                            except ValueError:

                                print(
                                    "INVALID TEMPERATURE DATA:",
                                    line
                                )

            else:

                time.sleep(0.05)

        except (serial.SerialException, OSError) as e:

            print("--------------------------------")
            print("SERIAL CONNECTION LOST")
            print(e)
            print("--------------------------------")

            try:

                if serial_connection:
                    serial_connection.close()

            except:
                pass

            serial_connection = None

            time.sleep(3)


# =========================
# DASHBOARD
# =========================

@app.route("/")
def dashboard():

    return render_template("dashboard.html")


# =========================
# API DATA
# =========================

@app.route("/api/data")
def api_data():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, temperature, status
        FROM temperature_readings
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()

    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            MAX(temperature) AS maximum,
            MIN(temperature) AS minimum
        FROM temperature_readings
    """)

    stats = cursor.fetchone()

    conn.close()

    readings = []

    for row in rows:

        readings.append({
            "timestamp": row["timestamp"],
            "temperature": row["temperature"],
            "status": row["status"]
        })

    readings.reverse()

    return jsonify({
        "success": True,
        "readings": readings,
        "total": stats["total"],
        "maximum": stats["maximum"],
        "minimum": stats["minimum"]
    })


# =========================
# CSV EXPORT
# =========================

@app.route("/export/csv")
def export_csv():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, temperature, status
        FROM temperature_readings
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    conn.close()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Timestamp",
        "Temperature (C)",
        "Status"
    ])

    for row in rows:

        writer.writerow([
            row["timestamp"],
            row["temperature"],
            row["status"]
        ])

    csv_data = output.getvalue()

    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=temperature_readings.csv"
        }
    )


# =========================
# ALERTS
# =========================

@app.route("/api/alerts")
def api_alerts():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, temperature, status
        FROM temperature_readings
        WHERE status IN ('WARNING', 'OVERHEATING')
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    alerts = []

    for row in rows:

        alerts.append({
            "timestamp": row["timestamp"],
            "temperature": row["temperature"],
            "status": row["status"]
        })

    return jsonify({
        "success": True,
        "alerts": alerts
    })


# =========================
# START APPLICATION
# =========================

if __name__ == "__main__":

    initialize_database()

    # Start serial reader
    serial_thread = threading.Thread(
        target=serial_reader,
        daemon=True
    )

    serial_thread.start()

    print("--------------------------------")
    print("PYROQUADCOM TEMPERATURE SYSTEM")
    print("--------------------------------")
    print("Serial Port:", SERIAL_PORT)
    print("Baud Rate:", BAUD_RATE)
    print("Website: http://localhost:5050")
    print("--------------------------------")

    app.run(
        host="0.0.0.0",
        port=5050,
        debug=True,
        use_reloader=False
    )