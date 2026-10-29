import serial
import time

PORT = "COM7"
BAUD_RATE = 9600

try:
    arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)

    print("Connected to Arduino Nano on", PORT)
    time.sleep(2)

    while True:
        if arduino.in_waiting > 0:
            data = arduino.readline().decode("utf-8", errors="ignore").strip()

            if data:
                print("Arduino:", data)

except serial.SerialException as e:
    print("Serial connection error:")
    print(e)

except KeyboardInterrupt:
    print("\nStopped.")

finally:
    try:
        arduino.close()
    except:
        pass