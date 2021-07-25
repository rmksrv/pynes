from abc import ABC
from typing import Optional

from pynes.core.bus import Bus


class Device(ABC):

    def __init__(self):
        self.bus: Optional[Bus] = None

    def connect_to_bus(self, bus: Bus) -> None:
        self.bus = bus
        self.bus.register_device(self)
