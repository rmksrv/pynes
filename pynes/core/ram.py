from ctypes import c_uint8, c_uint16, c_bool

from pynes.core.device.device import Device


class Ram(Device):

    SIZE_MEMORY:    c_uint16 = c_uint16(64 * 1024 - 1)
    INIT_VALUE_RAM: c_uint8  = c_uint8(0x00)

    def __init__(self):
        super().__init__()
        self.data = [Ram.INIT_VALUE_RAM for _ in range(Ram.SIZE_MEMORY.value)]
        self.bus = None

    def write(self, addr: c_uint16, data: c_uint8) -> None:
        if Ram.is_addr_valid(addr):
            self.data[addr.value].value = data.value

    def read(self, addr: c_uint16, read_only: c_bool = c_bool(False)) -> c_uint8:
        if Ram.is_addr_valid(addr):
            return self.data[addr.value]
        return Ram.INIT_VALUE_RAM

    @staticmethod
    def is_addr_valid(addr: c_uint16) -> bool:
        return 0x0000 <= addr.value < Ram.SIZE_MEMORY.value
