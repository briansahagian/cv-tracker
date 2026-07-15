# interpret pan and tilt angles and send to Arduino as motor commands

import serial
import time

# --- HARDWARE SETUP ---
# Uncomment the two lines below and change 'COM3' to your Arduino's port (e.g., '/dev/ttyACM0' on Mac/Linux)
# arduino_port = 'COM3' 
# baud_rate = 115200

# Initialize the serial connection (Uncomment below when ready for hardware)
# try:
#     arduino = serial.Serial(arduino_port, baud_rate, timeout=0.1)
#     time.sleep(2) # Give Arduino 2 seconds to reboot after connecting
# except Exception as e:
#     print(f"Warning: Could not connect to Arduino: {e}")
#     arduino = None

arduino = None
def send_to_arduino(pan_angle, tilt_angle):
    # Serial command format: <PanAngle,TiltAngle>

    data_packet = f"<{int(pan_angle)},{int(tilt_angle)}>\n"

    if arduino is non None and arduino.is_open:
        arduino.write(data_packet.encode('utf-8'))
    else:
        print(f"Simulated serial send: {data_packet.strip()}")