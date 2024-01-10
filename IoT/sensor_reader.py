# sensor_reader.py

import time
import threading
import warnings
from grove.grove_loudness_sensor import GroveLoudnessSensor
from grove.grove_light_sensor_v1_2 import GroveLightSensor
from GreenPonik_SHT40.SHT40 import SHT40

# Initialize sensors
loudness_sensor = GroveLoudnessSensor(4)
light_sensor = GroveLightSensor(2)
temp_humidity_sensor = SHT40()

# Shared data
data_lock = threading.Lock()
sensor_data = {
    'loudness': [],
    'light': [],
    'temperature': [],
    'humidity': []
}

# Ignore specific RuntimeWarning
warnings.filterwarnings("ignore", message="I2C frequency is not settable in python, ignoring!")

# Sensor reading functions
def read_loudness():
    while True:
        with data_lock:
            sensor_data['loudness'].append(loudness_sensor.value)
        time.sleep(1)

def read_light():
    while True:
        with data_lock:
            sensor_data['light'].append(light_sensor.light)
        time.sleep(1)

def read_temp_humidity():
    while True:
        try:
            temp, humid = temp_humidity_sensor.read_sht40()
            rounded_temp = round(temp, 1)
            rounded_humid = round(humid, 1)
            with data_lock:
                sensor_data['temperature'].append(temp)
                sensor_data['humidity'].append(humid)
        except Exception as e:
            print('Temp/Humidity sensor error: {}'.format(e))
        time.sleep(1)

def calculate_average(values):
    if not values or all(v is None for v in values):
        return None  # Or some default value, e.g., 0
    return round(sum(v for v in values if v is not None) / len(values), 1)

# Start reading sensors in threads
def start_sensor_threads():
    threads = []
    for func in [read_loudness, read_light, read_temp_humidity]:
        thread = threading.Thread(target=func)
        thread.start()
        threads.append(thread)
    return threads

if __name__ == '__main__':
    # If this script is run directly, start reading sensors
    start_sensor_threads()
