import random
import time
import logging
from datetime import datetime

# --- Constants (Calibration) ---
MIN_RSSI = -100
MAX_RSSI = 0
RSSI_THRESHOLD = -80
TOTAL_READINGS = 10
SLEEP_INTERVAL = 1  # seconds

# Configure professional logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_device_id() -> int:
    """Generates a random unique identifier for a device."""
    return random.randint(1, 1000)

def generate_reading(device_id: int) -> dict:
    """Creates a single telemetry data point"""
    rssi = random.randint(MIN_RSSI, MAX_RSSI)
    
    return {
        "device_id": device_id,
        "timestamp": datetime.now().isoformat(),
        "rssi": rssi,
        "status": "OK" if rssi > RSSI_THRESHOLD else "WARNING"
    }

def simulate_device_readings(device_id: int) -> None:
    """Orchestrates the simulation loop."""
    logging.info(f"Starting Simulation for Device ID: {device_id}")
    
    try:
        for i in range(1, TOTAL_READINGS + 1):
            reading = generate_reading(device_id)
            logging.info(f"Reading {i}/{TOTAL_READINGS}: {reading}")
            time.sleep(SLEEP_INTERVAL)
            
    except KeyboardInterrupt:
        logging.warning("\nSimulation interrupted by user.")

if __name__ == "__main__":
    current_device = get_device_id()
    simulate_device_readings(current_device)