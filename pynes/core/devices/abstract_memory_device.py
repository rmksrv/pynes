from ctypes import c_uint8, c_uint16

from pynes.core.devices import AbstractDevice


class AbstractMemoryDevice(AbstractDevice):

    SIZE_MEMORY: int = 64 * 1024 - 1
    INIT_VALUE:  int = 0x00

    def __init__(self):
        super().__init__()
        self.data = [c_uint8(AbstractMemoryDevice.INIT_VALUE) for _ in range(AbstractMemoryDevice.SIZE_MEMORY)]
        self.bus = None

    def write(self, addr: c_uint16, data: c_uint8) -> None:
        if AbstractMemoryDevice.is_addr_valid(addr):
            self.data[addr.value].value = data.value

    def read(self, addr: c_uint16, read_only: bool = False) -> c_uint8:
        if AbstractMemoryDevice.is_addr_valid(addr):
            return self.data[addr.value]
        return c_uint8(AbstractMemoryDevice.INIT_VALUE)

    @staticmethod
    def is_addr_valid(addr: c_uint16) -> bool:
        return 0x0000 <= addr.value < AbstractMemoryDevice.SIZE_MEMORY
