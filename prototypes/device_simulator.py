import random
import time
import logging
from datetime import datetime

# --- Constants (Calibration) ---
MIN_LATENCY_RANGE = 50  # ms
MAX_LATENCY_RANGE = 500  # ms
LATENCY_THRESHOLD = 300  # ms
MIN_RSSI = -100
MAX_RSSI = 0
RSSI_THRESHOLD = -80
BATTERY_CRITICAL_LEVEL = 15.0  # percentage
TOTAL_READINGS = 10
SLEEP_INTERVAL = 1  # seconds

# Configure professional logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_device_id() -> int:
    """Generates a random unique identifier for a device."""
    return random.randint(1, 1000)

def get_status(rssi: int, latency: int, battery_level: float) -> str:
    """Determines the status of the device based on telemetry data."""
    if battery_level < BATTERY_CRITICAL_LEVEL:
        return "CRITICAL"
    elif rssi < RSSI_THRESHOLD or latency > LATENCY_THRESHOLD:
        return "WARNING"
    else:
        return "OK"

def generate_reading(device_id: int) -> dict:
    """Creates a single telemetry data point"""
    rssi: int = random.randint(MIN_RSSI, MAX_RSSI)
    latency: int = random.randint(MIN_LATENCY_RANGE, MAX_LATENCY_RANGE)  # ms
    battery_level: float = round(random.uniform(0, 100),2)  # percentage

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
    
    try:
        for i in range(TOTAL_READINGS):
            reading = generate_reading(device_id)
            logging.info(f"Device {device_id} RSSI: {reading['rssi']}, Latency: {reading['latency']}, Battery Level: {reading['battery_level']}, Status: {reading['status']}")
            time.sleep(SLEEP_INTERVAL)
            
    except KeyboardInterrupt:
        logging.warning("\nSimulation interrupted by user.")

if __name__ == "__main__":
    current_device = get_device_id()
    simulate_device_readings(current_device)