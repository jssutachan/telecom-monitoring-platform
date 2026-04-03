import math

def calculate_airfiber_latency_dynamics(rssi: float, cinr: float, voltage: float, thresholds: dict) -> float:
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
    VOLTAGE_KNEE = thresholds.get("LOW_VOLTAGE_THRESHOLD", 23.5)
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

def calculate_airfiber_capacity_dynamics(rssi: float, cinr: float, voltage: float, thresholds: dict) -> float:
    """
    Orchestrates the capacity calculation based on Spectral Efficiency 
    and Hardware constraints.
    """
    max_cap = thresholds.get("MAX_CAPACITY")
    min_cap = thresholds.get("MIN_CAPACITY")
    
    # 1. Calculate the Modulation Factor (0.0 to 1.0) based on Signal Clarity
    # This represents how "dense" the data bits are.
    modulation_efficiency = _get_modulation_efficiency(cinr, rssi, thresholds)
    
    # 2. Calculate the Hardware Health Factor (0.0 to 1.0) based on Voltage
    # This represents MIMO chain stability and power-saving throttling.
    hardware_efficiency = _get_hardware_efficiency(voltage, thresholds)
    
    # 3. Final Calculation
    capacity = max_cap * modulation_efficiency * hardware_efficiency
    
    # Ensure we stay within physical bounds
    return round(max(min_cap, capacity), 2)

def _get_modulation_efficiency(cinr: float, rssi: float, thresholds: dict) -> float:
    """
    Simulates the MCS (Modulation and Coding Scheme) selection.
    Maps CINR/RSSI to a percentage of the theoretical maximum throughput.
    """

    # Base logic: If signal is perfect, efficiency is 100% (1.0)
    # If CINR drops below 20dB, we simulate the 'Modulation Staircase'
    if cinr >= thresholds.get("CINR_1024QAM_THRESHOLD") and rssi >= thresholds.get("RSSI_1024QAM_THRESHOLD"):
        return 1.0  # 1024QAM (10x)
    elif cinr >= thresholds.get("CINR_256QAM_THRESHOLD"):
        return 0.8  # 256QAM (8x)
    elif cinr >= thresholds.get("CINR_64QAM_THRESHOLD"):
        return 0.6  # 64QAM (6x)
    elif cinr >= thresholds.get("CINR_16QAM_THRESHOLD"):
        return 0.4  # 16QAM (4x)
    elif cinr >= thresholds.get("CINR_QPSK_THRESHOLD")or rssi >= thresholds.get("RSSI_QPSK_THRESHOLD"):
        return 0.2  # QPSK (2x)
    else:
        return 0.05 # 1x (SISO/Survival Mode)

def _get_hardware_efficiency(voltage: float, thresholds: dict) -> float:
    """
    Simulates the impact of low power on the Radio Chains (MIMO).
    At critical voltages, the radio may disable chains to stay alive.
    """
    v_low = thresholds.get("LOW_VOLTAGE_THRESHOLD")
    v_degraded = thresholds.get("DEGRADED_OPERATION_VOLTAGE_THRESHOLD")
    
    if voltage >= v_low:
        return 1.0 # 100% hardware capability
    
    # Between 21.5V and 23.5V: Moderate throttling (simulate 25% loss)
    if voltage > v_degraded:
        return 0.75
    
    # Below 21.5V: Critical throttling / MIMO chain shutdown (simulate 60% loss)
    # The radio is in "Emergency" mode.
    return 0.40

def calculate_airfiber_throughput_dynamics(rssi: float, cinr: float, voltage: float, capacity: float, thresholds: dict) -> float:
    # Adding 0.0 or 1.0 defaults here is the 'Safety Net'
    efficiency_multiplier = float(thresholds.get("PROTOCOL_EFFICIENCY", 0.92))
    min_throughput = float(thresholds.get("MIN_THROUGHPUT", 0.0))
    
    rf_loss = _calculate_rf_packet_loss(rssi, cinr, thresholds)
    processing_loss = _calculate_processing_loss(voltage, thresholds)
    
    # Debug print (Optional: Uncomment this to see exactly where it's failing)
    # print(f"DEBUG: Cap: {capacity} | Eff: {efficiency_multiplier} | RF Loss: {rf_loss} | Power Loss: {processing_loss}")

    # The Multiplicative Formula
    total_efficiency = efficiency_multiplier * (1.0 - rf_loss) * (1.0 - processing_loss)
    actual_throughput = capacity * total_efficiency
    
    return round(max(min_throughput, actual_throughput), 2)

def _calculate_rf_packet_loss(rssi: float, cinr: float, thresholds: dict) -> float:
    rssi_deg = float(thresholds.get("RSSI_THRESHOLD_DEGRADED", -75.0))
    rssi_min = float(thresholds.get("MIN_RSSI", -90.0)) 
    cinr_deg = float(thresholds.get("CINR_THRESHOLD_DEGRADED", 20.0))
    cinr_min = float(thresholds.get("MIN_CINR", 0.0))

    rssi_loss = 0.0
    if rssi < rssi_deg:
        danger_zone = abs(rssi_min) - abs(rssi_deg)
        if danger_zone > 0:
            current_depth = abs(rssi) - abs(rssi_deg)
            # Use min/max to keep the ratio between 0 and 1
            ratio = min(max(current_depth / danger_zone, 0.0), 1.0)
            rssi_loss = math.pow(ratio, 2)

    cinr_loss = 0.0
    if cinr < cinr_deg:
        danger_zone = cinr_deg - cinr_min
        if danger_zone > 0:
            current_depth = cinr_deg - cinr
            ratio = min(max(current_depth / danger_zone, 0.0), 1.0)
            cinr_loss = math.pow(ratio, 2)

    return min(1.0, max(rssi_loss, cinr_loss))

def _calculate_processing_loss(voltage: float, thresholds: dict) -> float:
    v_deg = float(thresholds.get("DEGRADED_OPERATION_VOLTAGE_THRESHOLD", 21.5))
    v_min = float(thresholds.get("MIN_VOLTAGE_OPERATIONAL_LIMIT", 21.0))
    
    if voltage >= v_deg:
        return 0.0
    
    span = v_deg - v_min
    if span > 0:
        depth = v_deg - voltage
        # Ensure loss doesn't exceed 0.5 (50%)
        loss = (depth / span) * 0.5 
        return min(0.5, max(0.0, loss))
    return 0.5