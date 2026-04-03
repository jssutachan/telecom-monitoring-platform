import math

def calculate_latency_dynamics(rssi: float, cinr: float, voltage: float, thresholds: dict) -> float:
    """
    Calculates dynamic latency using non-linear modeling.
    """
    base_latency = thresholds.get("BASE_LATENCY")
    
    # RSSI Constants
    RSSI_KNEE = thresholds.get("RSSI_THRESHOLD_DEGRADED")
    RSSI_COEFF = 0.15 # Controls the "spike" steepness
    
    # CINR Constants
    CINR_KNEE = thresholds.get("CINR_THRESHOLD_DEGRADED")
    CINR_DIVISOR = 10.0 # Normalization factor
    
    # Voltage Constants
    VOLTAGE_KNEE = thresholds.get("VOLTAGE_LOW_THRESHOLD", 23.5)
    VOLTAGE_EXPONENT = 2.5 # Severity of CPU lag
    VOLTAGE_MAX_PENALTY = 12.0 #Prevents infinite values.

    rssi_penalty = calculate_rssi_penalty(rssi, RSSI_KNEE, RSSI_COEFF)
    cinr_factor = calculate_cinr_factor(cinr, CINR_KNEE, CINR_DIVISOR)
    voltage_penalty = calculate_voltage_penalty(voltage, VOLTAGE_KNEE, VOLTAGE_EXPONENT, VOLTAGE_MAX_PENALTY)

    latency=(base_latency + rssi_penalty) * cinr_factor + voltage_penalty

    return round(latency, 2)

def calculate_rssi_penalty(rssi: float, rssi_knee: float, rssi_coeff: float) -> float:
    rssi_penalty = 0.0 
    if rssi < rssi_knee:
        # Penalize based on distance from the optimal signal floor
        diff = abs(rssi) - abs(rssi_knee)
        rssi_penalty = math.exp(rssi_coeff * diff) - 1.0
    return rssi_penalty

def calculate_cinr_factor(cinr: float, cinr_knee: float, cinr_divisor: float) -> float:
    cinr_factor = 1.0
    if cinr < cinr_knee:
        # Simulation of Packet Error Rate (PER) increasing as clarity drops
        cinr_factor = 1.0 + math.pow((cinr_knee - cinr) / cinr_divisor, 2)
    return cinr_factor

def calculate_voltage_penalty(voltage: float, voltage_knee: float, voltage_exponent: float, voltage_max_penalty: float)-> float:
    voltage_penalty = 0.0
    if voltage < voltage_knee:
        v_diff = voltage_knee - voltage
        # Power-law growth to simulate electronic "brownout" behavior
        voltage_penalty = min(voltage_max_penalty, math.pow(v_diff * 2, voltage_exponent))
    return voltage_penalty