import uuid
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class Device:
    """Base class for any IoT hardware in the network."""
    name: str #Format [Region]-[Type]-[ID]
    device_id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: str = "INIT"
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class AirFiberDevice(Device):
    """Specific subclass for Ubiquiti airFiber 5XHD hardware."""
    rssi: float = -55.0
    cinr: float = 30.0
    capacity_mbps: float = 600.0
    latency_ms: int = 5
    battery_voltage: float = 26.5

    def __post_init__(self):
        """Logic that runs right after the object is created."""
        # This ensures the parent class (Device) is also initialized correctly
        pass 

    def __repr__(self):
        return f"<AirFiber {self.name} | RSSI: {self.rssi}dBm | Bat: {self.battery_voltage}V>"

d1= AirFiberDevice(name="US-East-AirFiber-001")
print(d1)
