import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import ClassVar

class InvalidDeviceConfigError(Exception):
    """Raised when a device is created with invalid data."""
    pass

class InvalidDeviceStatusError(Exception):
    """Raised when an invalid status is assigned to a device."""
    pass

class InvalidDeviceRSSI(Exception):
    """Raised when an invalid RSSI value is assigned to a device."""
    pass

@dataclass
class Device:
    """Base class for any hardware in the network."""
    APPROVED_REGIONS: ClassVar[set] = {"BOG", "MED", "CLO", "BAQ", "BUC", "PEI", "CTG", "VVC", "SMR", "CUC"}
    APPROVED_CARDINALS: ClassVar[set] = {"NORTH", "SOUTH", "EAST", "WEST", "NORTHEAST", "NORTHWEST", "SOUTHEAST", "SOUTHWEST"}
    APPROVED_DEVICES: ClassVar[set] = {"AIRFIBER5XHD"}

    name: str #Format [Cardinal]-[Region]-[Type]-[ID]
    cardinal: str = field(init=False)
    region: str = field(init=False)
    device_id: uuid.UUID = field(default_factory=uuid.uuid4)
    _status: str = "INIT"
    last_updated: datetime = field(default_factory=datetime.now)
    number_of_devices: ClassVar[int]= 0
    parts: list = field(init=False)

    def __post_init__(self):
        self.parts = self.name.split("-")
        self._validate_object_creation()
        Device.number_of_devices += 1

    def _validate_object_creation(self):
        self._validate_name_format()
        self._validate_region_and_cardinal()
        self._validate_device()

    def _validate_name_format(self):
        if len(self.parts) != 4:
            raise InvalidDeviceConfigError(f"Device name '{self.name}' must have exactly 4 parts separated by dashes (Cardinal-Region-Type-ID).")

    def _validate_region_and_cardinal(self):
        parsed_cardinal = self.parts[0].upper()
        parsed_region = self.parts[1].upper()

        if parsed_cardinal not in Device.APPROVED_CARDINALS:
            raise InvalidDeviceConfigError(f"Cardinal '{parsed_cardinal}' is not in the approved list: {Device.APPROVED_CARDINALS}")
        
        if parsed_region not in Device.APPROVED_REGIONS:
            raise InvalidDeviceConfigError(f"Region '{parsed_region}' is not in the approved list: {Device.APPROVED_REGIONS}")
        
        self.cardinal = parsed_cardinal.upper()
        self.region = parsed_region.upper()

    def _validate_device(self):
        if self.parts[2].upper() not in Device.APPROVED_DEVICES:
            raise InvalidDeviceConfigError(f"Device type '{self.parts[2]}' is not in the approved list: {Device.APPROVED_DEVICES}")

    def __repr__(self):
        return f"{self.last_updated} Device({self.name}: Cardinal = {self.cardinal} | Region = {self.region} | Status = {self.status})"


@dataclass
class AirFiber5XHD(Device):
    """Specific subclass for Ubiquiti airFiber 5XHD hardware."""

    MAX_RSSI: ClassVar[float] = -30.0 #dBm
    RSSI_THRESHOLD_DEGRADED: ClassVar[float] = -85.0 #dBm
    MIN_RSSI: ClassVar[float] = -90.0 #dBm

    MAX_CINR: ClassVar[float] = 35.0 #dB
    CINR_THRESHOLD_DEGRADED: ClassVar[float] = 20.0 #dB|
    MIN_CINR: ClassVar[float] = 0.0 #dB

    MAX_CAPACITY: ClassVar[float] = 1200.0 #mbps
    MIN_CAPACITY: ClassVar[float] = 0.0 #mbps

    MIN_THROUGHPUT: ClassVar[float] = 0.0 #mbps

    MAX_VOLTAGE_LIMIT: ClassVar[float] = 54.0 #volts
    NOMINAL_VOLTAGE: ClassVar[float] = 24.0 #volts
    MIN_VOLTAGE_OPERATIONAL: ClassVar[float] = 19.0 #volts
    CRITICAL_VOLTAGE_OFFLINE: ClassVar[float] = 18.5 #volts
    BATT_FULL_VOLTAGE: ClassVar[float] = 27.2 #volts
    BATT_LOW_VOLTAGE: ClassVar[float] = 22.5 #volts
    BATT_EMPTY_VOLTAGE: ClassVar[float] = 21.0 #volts
    
    rssi: float = -55.0
    cinr: float = 30.0
    capacity: float = 600.0 #mbps
    latency: int = 5 #ms
    throughput: float = 550.0 #mbps
    battery: float = 26.5 #volts
    number_of_airfiber: ClassVar[int] = 0

    def __post_init__(self):
        """Logic that runs right after the object is created."""
        super().__post_init__()
        AirFiber5XHD.number_of_airfiber += 1  

    def __repr__(self):
        return f"{self.last_updated} AirFiber5XHD({self.name.upper()}: rssi = {self.rssi} dBm | cinr = {self.cinr} dB | battery = {self.battery} V | status = {self.status} | capacity = {self.capacity} mbps \n latency = {self.latency} ms | throughput = {self.throughput} Mbps)"

    @property
    def status(self ) -> str:
        return self._status
    
    @status.setter  
    def status(self, new_value: str):
        valid_statuses = {"INIT", "ONLINE", "MAINTENANCE", "DEGRADED", "OFFLINE", "LOW BATTERY", "LOW BATTERY AND DEGRADED"}
        if new_value.upper() not in valid_statuses:
            raise InvalidDeviceStatusError(f"Status '{new_value}' is not valid. Must be one of: {valid_statuses}")
        if self._status != new_value.upper():
            print(f"Log: {self.name} changed from {self._status} to {new_value.upper()}")
            self._status = new_value.upper()
            self.last_updated = datetime.now()

    def update_metrics(self, new_rssi: float, new_cinr: float, new_capacity: float, new_latency: int, new_throughput: float, new_voltage: float, is_in_maintenance: bool = False):
        """Update performance metrics and automate status changes based on hardware voltage limits and signal quality."""
        # 1. Physical Attribute Assignment
        self.voltage = new_voltage
        self.rssi = new_rssi
        self.cinr = new_cinr
        self.capacity = new_capacity
        self.latency = new_latency
        self.throughput = new_throughput
    
        # 2. Status Automation Logic
        # Maintenance has the highest priority
        if is_in_maintenance:
            self.status = "MAINTENANCE"
            return

        # Voltage-based critical failures
        if self.voltage < self.CRITICAL_VOLTAGE_OFFLINE:
            self.status = "OFFLINE"
            # Optional: Zero out telemetry if offline
            self.capacity = 0
            self.throughput = 0
            return

        # Signal Quality Thresholds (Constants for readability)
        is_degraded = self.rssi < -85.0 or self.cinr < 20.0
        # Defining 'Low Battery' as anything approaching the operational limit (e.g., < 22.5V)
        is_low_battery = self.voltage <= self.BATT_LOW_VOLTAGE 

        # 3. State Machine Logic
        if is_low_battery and is_degraded:
            self.status = "LOW BATTERY AND DEGRADED"
        elif is_low_battery:
            self.status = "LOW BATTERY"
        elif is_degraded:
            self.status = "DEGRADED"
        else:
            self.status = "ONLINE"

    def get_device_online(self, online: bool):
        if self._status == "INIT" and online:
            self._status = "ONLINE"
            self.update_metrics(new_rssi=self.rssi, new_cinr=self.cinr, new_capacity=self.capacity, new_latency=self.latency, new_throughput=self.throughput, new_battery=self.battery)
            print(f"Log: {self.name} is now ONLINE")
        elif self._status == "INIT" and not online:
            print(f"Log: {self.name} is now initializing")
        else:
            print(f"Log: {self.name} is already {self._status}")     
    
    #@property
    #def rssi(self) -> float:
    #    return self._rssi
    
   # @rssi.setter
    #    def rssi(self, new_value: float):

d1= AirFiber5XHD(name="south-ctg-AIRFIBER5XHd-001")
print(d1)
