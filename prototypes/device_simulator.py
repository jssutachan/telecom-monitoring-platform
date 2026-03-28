import random
import time
import logging
from datetime import datetime

# --- Constants (Calibration) ---
MIN_LATENCY_RANGE: int = 50  # ms
MAX_LATENCY_RANGE: int = 500  # ms
MAX_LATENCY_SHIFT: int = 50  # (absolut) maximum change in latency per reading ms
LATENCY_THRESHOLD: int = 300  # ms A reading above this latency is considered a warning

MIN_RSSI: int = -100 #dBm
MAX_RSSI: int = 0   #dBm
MAX_RSSI_SHIFT: int = 5  # (absolut) maximum change in RSSI per reading dBm
RSSI_THRESHOLD: int = -80   #dBm A reading below this RSSI is considered a warning

MIN_BATTERY_LEVEL: float = 0.0  # percentage
MAX_BATTERY_LEVEL: float = 100.0  # percentages
BATTERY_CRITICAL_LEVEL: float = 15.0  # percentage A reading below this battery level is considered critical
BATTERY_DECAY_PER_READING: float = 5.0  # percentage decrease per reading
 
TOTAL_READINGS: int = 10
SLEEP_INTERVAL: float = 1.0 # seconds

# --- Simulation Setup ---
device_id: int =random.randint(1, 1000)
## Use the following lines to use fixed initial values instead of random ones, you'll need to also check the lines from 79 to 87
INITIAL_RSSI: int = -90 #dBm must be between MIN_RSSI and MAX_RSSI
INITIAL_LATENCY: int = 120  # ms must be between MIN_LATENCY_RANGE and MAX_LATENCY_RANGE
INITIAL_BATTERY_LEVEL: float = round(100.0, 2)  # percentage must be between MIN_BATTERY_LEVEL and MAX_BATTERY_LEVEL

# Configure professional logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_status(rssi: int, latency: int, battery_level: float) -> str:
    """Determines the status of the device based on telemetry data."""
    if battery_level < BATTERY_CRITICAL_LEVEL:
        return "CRITICAL"
    elif rssi < RSSI_THRESHOLD or latency > LATENCY_THRESHOLD:
        return "WARNING"
    else:
        return "OK"

def calculate_new_rssi(rssi: int)-> int:
    """Simulates a new RSSI value based on the previous reading."""
    change = random.randint(-MAX_RSSI_SHIFT, MAX_RSSI_SHIFT)    # Simulate small fluctuations
    new_rssi = rssi + change
    return max(MIN_RSSI, min(MAX_RSSI, new_rssi))

def calculate_new_latency(latency: int) -> int:
    """Simulates a new latency value based on the previous reading."""
    change = random.randint(-MAX_LATENCY_SHIFT, MAX_LATENCY_SHIFT)  # Simulate small fluctuations
    new_latency = latency + change
    return max(MIN_LATENCY_RANGE, min(MAX_LATENCY_RANGE, new_latency))

def simulate_battery_decay(battery_level: float) -> float:
    """Simulates battery decay by decreasing the battery level by a consistent configurable amount."""
    new_battery_level = battery_level - BATTERY_DECAY_PER_READING
    return max(MIN_BATTERY_LEVEL, min(MAX_BATTERY_LEVEL, new_battery_level))

def generate_reading(device_id: int, rssi: int, latency: int, battery_level: float) -> dict:
    """Creates a dictionary representing a single telemetry reading for the device."""
    return {
        "device_id": device_id,
        "timestamp": datetime.now().isoformat(),
        "rssi": rssi,
        "latency": latency,
        "battery_level": battery_level,
        "status": get_status(rssi, latency, battery_level)
    }

def simulate_device_readings(device_id: int) -> None:
    """Orchestrates the simulation loop."""
    logging.info(f"Starting Simulation for Device ID: {device_id}")

    ## Use the following lines to set random initial values, if so uncomment lines from 77 to 79 and comment lines from 81 to 83 and lines 28 to 30.
    #rssi = random.randint(MIN_RSSI, MAX_RSSI)
    #latency = random.randint(MIN_LATENCY_RANGE, MAX_LATENCY_RANGE)
    #battery_level = round(random.uniform(MIN_BATTERY_LEVEL, MAX_BATTERY_LEVEL), 2)

    ## Use the following lines to set fixed initial values, if so uncomment lines from 81 to 83 and comment lines from 77 to 79 and make sure to set the INITIAL_RSSI, INITIAL_LATENCY and INITIAL_BATTERY_LEVEL constants to the desired values
    rssi = INITIAL_RSSI
    latency = INITIAL_LATENCY
    battery_level = INITIAL_BATTERY_LEVEL  

    try:
        for i in range(TOTAL_READINGS):
            reading = generate_reading(device_id, rssi, latency, battery_level)
            logging.info(f"Device {device_id} RSSI: {reading['rssi']} dBm, Latency: {reading['latency']} ms, Battery Level: {reading['battery_level']} %, Status: {reading['status']}")
            rssi = calculate_new_rssi(rssi)
            latency = calculate_new_latency(latency)
            battery_level = simulate_battery_decay(battery_level)
            time.sleep(SLEEP_INTERVAL)
            
    except KeyboardInterrupt:
        logging.warning("\nSimulation interrupted by user.")

if __name__ == "__main__":
    simulate_device_readings(device_id)