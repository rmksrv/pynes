from ctypes import c_ubyte, c_ushort, c_uint
from typing import List


class Memory:
    MAX_MEMORY: int = 1024 * 64

    def __init__(self):
        self.data: List[c_ubyte] = [c_ubyte(0x00) for _ in range(Memory.MAX_MEMORY)]

    def clear(self):
        self.data = [c_ubyte(0x00) for _ in range(Memory.MAX_MEMORY)]

    def read_byte(self, addr: int) -> c_ubyte:
        if Memory.is_valid_address(addr):
            return self.data[addr]
        return c_ubyte(0x00)

    def write_byte(self, addr: int, data: c_ubyte) -> None:
        if Memory.is_valid_address(addr):
            self.data[addr] = data

    def write_word(self, addr: int, data: c_ushort, cycles: c_uint) -> None:
        if Memory.is_valid_address(addr):
            self.data[addr] = c_ubyte(data.value & 0xFF)
            self.data[addr + 1] = c_ubyte(data.value >> 8)
            cycles.value -= 2

    @staticmethod
    def is_valid_address(addr: int):
        return 0x0000 <= addr < Memory.MAX_MEMORY
