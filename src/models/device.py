import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import ClassVar

class InvalidDeviceConfigError(Exception):
    """Raised when a device is created with invalid regional data."""
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
    status: str = "INIT"
    last_updated: datetime = field(default_factory=datetime.now)
    number_of_devices: ClassVar[int]= 0

    def __post_init__(self):
        self.validate_region_and_cardinal()
        Device.number_of_devices += 1

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
    battery: float = 26.5 #volts
    number_of_airfiber: ClassVar[int] = 0

    def __post_init__(self):
        """Logic that runs right after the object is created."""
        super().__post_init__()
        AirFiber5XHD.number_of_airfiber += 1

    def __repr__(self):
        return f"{self.last_updated} AirFiber5XHD({self.name.upper()}: rssi={self.rssi} | status='{self.status}')"
