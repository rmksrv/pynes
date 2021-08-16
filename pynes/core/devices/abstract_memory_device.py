from ctypes import c_uint8, c_uint16
from abc import abstractmethod
from functools import wraps

from pynes.core.devices import AbstractDevice
from pynes.core.exceptions import OutOfRangeMemoryException


class AbstractMemoryDevice(AbstractDevice):
    INIT_VALUE:   int = 0x00
    ABS_MIN_ADDR: int = 0x0000
    ABS_MAX_ADDR: int = 0xffff

    @property
    @abstractmethod
    def min_address(self) -> int:
        pass

    @property
    @abstractmethod
    def max_address(self) -> int:
        pass

    @property
    def size_memory(self) -> int:
        return self.max_address - self.min_address + 1

    def __init__(self):
        super().__init__()
        self.data = [c_uint8(AbstractMemoryDevice.INIT_VALUE) for _ in range(self.size_memory)]
        self.bus = None

    def write(self, addr: c_uint16, data: c_uint8) -> None:
        if self.is_address_valid(addr):
            self.data[addr.value - self.min_address].value = data.value

    def read(self, addr: c_uint16, read_only: bool = False) -> c_uint8:
        if self.is_address_valid(addr):
            return self.data[addr.value - self.min_address]
        return c_uint8(AbstractMemoryDevice.INIT_VALUE)

    def is_address_valid(self, addr: c_uint16) -> bool:
        return self.min_address <= addr.value <= self.max_address
