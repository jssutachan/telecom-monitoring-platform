import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import ClassVar

class InvalidDeviceConfigError(Exception):
    """Raised when a device is created with invalid regional data."""
    pass

class InvalidDeviceStatusError(Exception):
    """Raised when an invalid status is assigned to a device."""
    pass

@dataclass
class Device:
    """Base class for any hardware in the network."""
    APPROVED_REGIONS: ClassVar[set] = {"BOG", "MED", "CLO", "BAQ", "BUC", "PEI", "CTG", "VVC", "SMR", "CUC"}
    APPROVED_CARDINALS: ClassVar[set] = {"NORTH", "SOUTH", "EAST", "WEST", "NORTHEAST", "NORTHWEST", "SOUTHEAST", "SOUTHWEST"}

    name: str #Format [Cardinal]-[Region]-[Type]-[ID]
    cardinal: str = field(init=False)
    region: str = field(init=False)
    device_id: uuid.UUID = field(default_factory=uuid.uuid4)
    _status: str = "INIT"
    last_updated: datetime = field(default_factory=datetime.now)
    number_of_devices: ClassVar[int]= 0

    def __post_init__(self):
        self.validate_region_and_cardinal()
        Device.number_of_devices += 1

    def __repr__(self):
        return f"{self.last_updated} Device({self.name}: Cardinal = {self.cardinal} | Region = {self.region} | Status = {self.status})"


    def validate_region_and_cardinal(self):
        parts = self.name.split("-")
    
        if len(parts) < 4:
            raise InvalidDeviceConfigError(f"Device name '{self.name}' must have at least 4 parts separated by '-'")
        parsed_cardinal = parts[0].upper()
        parsed_region = parts[1].upper()

        if parsed_cardinal not in Device.APPROVED_CARDINALS:
            raise InvalidDeviceConfigError(f"Cardinal '{parsed_cardinal}' is not in the approved list: {Device.APPROVED_CARDINALS}")
        
        if parsed_region not in Device.APPROVED_REGIONS:
            raise InvalidDeviceConfigError(f"Region '{parsed_region}' is not in the approved list: {Device.APPROVED_REGIONS}")
        
        self.cardinal = parsed_cardinal
        self.region = parsed_region

@dataclass
class AirFiber5XHD(Device):
    """Specific subclass for Ubiquiti airFiber 5XHD hardware."""
    
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

    def update_metrics(self, new_rssi: float, new_cinr: float, new_capacity: float, new_latency: int, new_throughput: float, new_battery: float, is_in_maintenance: bool = False):
        """Update the performance metrics of the AirFiber device."""
        self.rssi = new_rssi
        self.cinr = new_cinr
        self.capacity = new_capacity
        self.latency = new_latency
        self.throughput = new_throughput
        self.battery = new_battery

        if is_in_maintenance:
            self.status = "MAINTENANCE"
        elif self.battery<=21.0:
            self.status = "OFFLINE"
        elif 21.0 < self.battery <= 22.5 and self.rssi > -85.0 and self.cinr > 20.0:
            self.status = "LOW BATTERY"
        elif 22.5 < self.battery <= 26.5 and (self.rssi < -85.0 or self.cinr < 20.0):
            self.status = "LOW BATTERY AND DEGRADED"
        elif self.rssi < -85.0 or self.cinr < 20.0:
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
