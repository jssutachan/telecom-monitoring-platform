import uuid
from datetime import datetime
from dataclasses import dataclass, field, InitVar
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

class InvalidDeviceCINR(Exception):
    """Raised when an invalid CINR value is assigned to a device."""
    pass

class InvalidDeviceBattery(Exception):
    """Raised when an invalid battery voltage is assigned to a device."""
    pass

@dataclass
class Device:
    """Base class for any hardware in the network."""

    # Class-level constants for validation

    APPROVED_REGIONS: ClassVar[set] = {"BOG", "MED", "CLO", "BAQ", "BUC", "PEI", "CTG", "VVC", "SMR", "CUC"}
    APPROVED_CARDINALS: ClassVar[set] = {"NORTH", "SOUTH", "EAST", "WEST", "NORTHEAST", "NORTHWEST", "SOUTHEAST", "SOUTHWEST"}
    APPROVED_DEVICES: ClassVar[set] = {"AIRFIBER5XHD"}

    # Class-level attributes for tracking devices

    _number_of_devices: ClassVar[int]= 0
    _name_registry: ClassVar[set] = set() # To track unique device names
    
    # Instance attributes

    name: InitVar[str] #Format [Cardinal]-[Region]-[Type]-[ID]
    _name: str = field(init=False)
    _device_id: uuid.UUID = field(default_factory=uuid.uuid4)
    _last_updated: datetime = field(default_factory=datetime.now)
    _cardinal: str = field(init=False)
    _region: str = field(init=False)
    _status: str = field(default="INIT")
    _is_initializing: bool = field(default=True)
    _in_maintenance: bool = field(default=False)
    _parts: list = field(init=False)

    # __post_init__ method 

    def __post_init__(self, name: str) -> None:
        self._name = name.upper()
        self._parts = self._name.split("-")
        cardinal = self._parts[0]
        region = self._parts[1]

        self._validate_name_format()

        self.cardinal = cardinal
        self.region = region

        self._validate_device()
        self._register_device()

        Device._number_of_devices += 1

    # Properties and validation methods

    @property
    def name(self) -> str:
        return self._name

    @property
    def device_id(self) -> uuid.UUID:
        return self._device_id
    
    @property
    def last_updated(self) -> datetime:
        return self._last_updated   

    @property
    def is_initializing(self) -> bool:
        return self._is_initializing
    @is_initializing.setter
    def is_initializing(self, value: bool) -> None:
        self._is_initializing = value

    @property
    def in_maintenance(self) -> bool:
        return self._in_maintenance
    @in_maintenance.setter
    def in_maintenance(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError(f"in_maintenance must be a boolean value, got {type(value)}")
        self._in_maintenance = value

    @property
    def cardinal(self) -> str:
        return self._cardinal
    
    @cardinal.setter
    def cardinal(self, cardinal: str) -> None:
        if cardinal not in Device.APPROVED_CARDINALS:
            raise InvalidDeviceConfigError(f"Cardinal '{cardinal}' is not in the approved list: {Device.APPROVED_CARDINALS}")
        self._cardinal = cardinal

    @property
    def region(self) -> str:
        return self._region
    
    @region.setter
    def region(self, region: str) -> None:
        if region not in Device.APPROVED_REGIONS:
            raise InvalidDeviceConfigError(f"Region '{region}' is not in the approved list: {Device.APPROVED_REGIONS}")
        self._region = region

    @property
    def status(self) -> str:
        return self._status
    
    @status.setter
    def status(self, new_status: str) -> None:
        valid_statuses = {"INIT", "ONLINE", "MAINTENANCE", "DEGRADED", "OFFLINE"}
        if new_status.upper() not in valid_statuses:
            raise InvalidDeviceStatusError(f"Status '{new_status}' is not valid. Must be one of: {valid_statuses}")
        if self._status != new_status.upper():
            print(f"Log: {self.name} changed from {self._status} to {new_status.upper()}")
            self._status = new_status.upper()
            self._last_updated = datetime.now()
            print(self)

    #Private helper methods

    def _validate_name_format(self) -> None:
        if len(self._parts) != 4:
            raise InvalidDeviceConfigError(f"Device name '{self.name}' must have exactly 4 parts separated by dashes (Cardinal-Region-Type-ID).")

    def _validate_device(self) -> None:
        """Checks if the hardware type is supported."""
        device_type = self._parts[2]
        if device_type not in Device.APPROVED_DEVICES:
            raise InvalidDeviceConfigError(
                f"Device type '{device_type}' is not supported. "
                f"Allowed: {Device.APPROVED_DEVICES}"
            )

    def _register_device(self) -> None:
        """Ensures uniqueness and updates regional counters."""
        name = self._name
        
        if name in Device._name_registry:
            raise InvalidDeviceConfigError(
                f"Conflict: Device '{name}' already exists in the registry."
            )
        Device._name_registry.add(name)
    
    #Special methods 

    def __repr__(self) -> str:
        return f"{self.last_updated} Device({self.name}: Cardinal = {self.cardinal} | Region = {self.region} | Status = {self.status})"

    def finish_startup(self) -> None:
        """Call this method to mark the device as finished initializing."""
        self.is_initializing = False
        status = input("Enter new status: ")
        self.status = status

    def set_maintenance_mode(self, enabled: bool):
        """Technician overrida. Higher priority than any sensor data"""
        self.in_maintenance = enabled
        if enabled:
            self.status = "MAINTENANCE"
        else:
            status = input("Enter new status: ")
            self.status = status

@dataclass
class AirFiber5XHD(Device):
    """Specific subclass for Ubiquiti airFiber 5XHD hardware."""

    # Class-level constants for performance thresholds

    #RSSI thresholds
    MAX_RSSI: ClassVar[float] = -30.0 #dBm
    RSSI_THRESHOLD_DEGRADED: ClassVar[float] = -75.0 #dBm
    MIN_RSSI: ClassVar[float] = -90.0 #dBm

    #CINR thresholds
    MAX_CINR: ClassVar[float] = 35.0 #dB
    CINR_THRESHOLD_DEGRADED: ClassVar[float] = 20.0 #dB|
    MIN_CINR: ClassVar[float] = 0.0 #dB

    #Capacity and Throughput thresholds
    MAX_CAPACITY: ClassVar[float] = 1200.0 #mbps
    MIN_CAPACITY: ClassVar[float] = 0.0 #mbps
    MIN_THROUGHPUT: ClassVar[float] = 0.0 #mbps

    #Voltage thresholds
    MAX_VOLTAGE_LIMIT: ClassVar[float] = 54.0 #volts
    NOMINAL_VOLTAGE: ClassVar[float] = 24.0 #volts
    MIN_VOLTAGE_OPERATIONAL: ClassVar[float] = 19.0 #volts
    CRITICAL_VOLTAGE_OFFLINE: ClassVar[float] = 18.5 #volts

    #Battery thresholds
    BATT_FULL_VOLTAGE: ClassVar[float] = 27.2 #volts
    BATT_LOW_VOLTAGE: ClassVar[float] = 23.5 #volts
    BATT_CRITICAL_VOLTAGE: ClassVar[float] = 21.5 #volts
    BATT_EMPTY_VOLTAGE: ClassVar[float] = 21.0 #volts
    MIN_BATTERY: ClassVar[float] = 0.0 # %
    MAX_BATTERY: ClassVar[float] = 100.0 # %

    # Instance attributes with default values
    _rssi: float = -55.0
    _cinr: float = 30.0
    _capacity: float = 600.0 #mbps
    _latency: int = 5 #ms
    _throughput: float = 550.0 #mbps
    _voltage: float = 24.0 #volts
    _battery: float = 100.0 # %
    _number_of_airfiber: ClassVar[int] = 0

    # Override __post_init__ to set specific defaults and track AirFiber instances

    def __post_init__(self, name: str) -> None:
        """Logic that runs right after the object is created."""
        super().__post_init__(name)
        max_throughput = self.capacity
        AirFiber5XHD._number_of_airfiber += 1  

    # Properties and validation methods for AirFiber-specific attributes

    @property
    def rssi(self) -> float:
        return self._rssi
    @rssi.setter
    def rssi(self, value: float) -> None:
        if not (AirFiber5XHD.MIN_RSSI <= value <= AirFiber5XHD.MAX_RSSI):
            raise InvalidDeviceRSSI(f"RSSI value {value} dBm is out of valid range ({AirFiber5XHD.MIN_RSSI} to {AirFiber5XHD.MAX_RSSI} dBm).")
        self._rssi = value

    @property
    def cinr(self) -> float:
        return self._cinr
    @cinr.setter
    def cinr(self, value: float) -> None:
        if not (AirFiber5XHD.MIN_CINR <= value <= AirFiber5XHD.MAX_CINR):
            raise InvalidDeviceCINR(f"CINR value {value} dB is out of valid range ({AirFiber5XHD.MIN_CINR} to {AirFiber5XHD.MAX_CINR} dB).")
        self._cinr = value

    @property
    def voltage(self) -> float:
        return self._voltage
    @voltage.setter
    def voltage(self, value: float) -> None:
        if not (AirFiber5XHD.CRITICAL_VOLTAGE_OFFLINE <= value <= AirFiber5XHD.MAX_VOLTAGE_LIMIT):
            raise InvalidDeviceBattery(f"Battery voltage {value} V is out of valid range ({AirFiber5XHD.CRITICAL_VOLTAGE_OFFLINE} to {AirFiber5XHD.MAX_VOLTAGE_LIMIT} V).")
        self._voltage = value

    @property  
    def battery(self) -> float:
        return self._battery
    @battery.setter
    def battery(self, value: float) -> None:
        if not (AirFiber5XHD.MIN_BATTERY <= value <= AirFiber5XHD.MAX_BATTERY):
            raise InvalidDeviceBattery(f"Battery voltage {value} % is out of valid range ({AirFiber5XHD.MIN_BATTERY} to {AirFiber5XHD.MAX_BATTERY} %).")
        self._battery = value

    @property
    def capacity(self) -> float:
        return self._capacity
    @capacity.setter
    def capacity(self, value: float) -> None:
        if not (AirFiber5XHD.MIN_CAPACITY <= value <= AirFiber5XHD.MAX_CAPACITY):
            raise ValueError(f"Capacity {value} Mbps is out of valid range ({AirFiber5XHD.MIN_CAPACITY} to {AirFiber5XHD.MAX_CAPACITY} Mbps).")
        self._capacity = value

    @property
    def throughput(self) -> float:
        return self._throughput
    @throughput.setter
    def throughput(self, value: float) -> None:
        if not (AirFiber5XHD.MIN_THROUGHPUT <= value <= AirFiber5XHD.max_throughput):
            raise ValueError(f"Throughput {value} Mbps is out of valid range ({AirFiber5XHD.MIN_THROUGHPUT} to {AirFiber5XHD.max_throughput} Mbps).")
        self._throughput = value

    @property
    def latency(self) -> int:
        return self._latency
    @latency.setter
    def latency(self, value: int) -> None:
        if not (AirFiber5XHD.MIN_LATENCY <= value <= AirFiber5XHD.MAX_LATENCY):
            raise ValueError(f"Latency {value} ms is out of valid range ({AirFiber5XHD.MIN_LATENCY} to {AirFiber5XHD.MAX_LATENCY} ms).")
        self._latency = value

    # Private helper methods

    def update_metrics(self, rssi: float, cinr: float, battery: float) -> None:
        self.rssi = rssi
        self.cinr = cinr
        self.battery = battery
        self.update_status_based_on_performance()

    def update_status_based_on_performance(self) -> None:
        if self.device_is_under_maintenance():
            self.status = "MAINTENANCE"
        elif self.device_is_offline():
            self.status = "OFFLINE"
        elif self.device_is_initializing():
            self.status = "INIT"
        elif self.device_is_low_battery():
            self.status = "LOWBATTERY"
        elif self.device_is_degraded():
            self.status = "DEGRADED"
        elif self.device_is_online():
            self.status = "ONLINE"

    def device_is_under_maintenance(self) -> bool:
        if self.status == "MAINTENANCE" and self.is_in_maintenance():
            return True
        else:
            return False

    def device_is_offline(self) -> bool:
        """
        Critical Failure: The link has dropped or hardware has shut down.
        Logic: RSSI below minimum OR CINR below minimum OR Voltage at critical cutoff.
        """
        return (self.rssi <= AirFiber5XHD.MIN_RSSI or
                self.cinr <= AirFiber5XHD.MIN_CINR or
                self.voltage <= AirFiber5XHD.CRITICAL_VOLTAGE_OFFLINE)
    
    def device_is_initializing(self) -> bool:
        if self.status == "INIT":
            return True
        else:
            return False
    
    def device_is_low_battery(self) -> bool:
        """
        Infrastructure Warning: Power level is between critical and operational.
        Logic: Battery percentage between 6% and 10%.
        """
        return AirFiber5XHD.CRITICAL_VOLTAGE_OFFLINE < self.voltage <=self.BARR_LOW_VOLTAGE
        
    def connection_is_degradedl(self) -> bool:
        """
        Performance Alert: Link is functional but experiencing interference or fading.
        Logic: Any metric falls below the primary threshold but above the minimum.
        """
        return (self.rssi_fail() or self.cinr_fail() or self.voltage_fail())
    
    def rssi_fail(self) -> bool:
        return self.MIN_RSSI < self.rssi <= self.RSSI_THRESHOLD_DEGRADED
    
    def cinr_fail(self) -> bool:
        return self.MIN_CINR < self.cinr <= self.CINR_THRESHOLD_DEGRADED

    def voltage_fail(self) -> bool:
        return self.BATT_LOW_VOLTAGE < self.voltage <= self.MIN_VOLTAGE_OPERATIONAL

    def device_is_online(self) -> bool:
        """
        Optimal State: All metrics exceed their degraded thresholds.
        """
        return (self.rssi > AirFiber5XHD.RSSI_THRESHOLD_DEGRADED and
                self.cinr > AirFiber5XHD.CINR_THRESHOLD_DEGRADED and
                self.voltage > AirFiber5XHD.BATT_LOW_VOLTAGE)
    

    # Special methods override __repr__ to include AirFiber-specific details
    def __repr__(self) -> str:
        return (f"{self.last_updated} AirFiber5XHD({self.name}: RSSI = {self.rssi} dBm | CINR = {self.cinr} dB | Battery = {self.battery} % | Status = {self.status} \n "
                f"Capacity = {self.capacity} Mbps | Latency = {self.latency} ms | Throughput = {self.throughput} Mbps ")    
