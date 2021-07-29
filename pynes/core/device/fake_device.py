from abc import ABC, abstractmethod
from ctypes import c_uint16, c_uint8
from typing import Dict, Any


class FakeDevice(ABC):
    """
    tl;dr: FakeDevice == Device
    Duplicating class for device.Device. Need this one to avoid circular imports, e.g.:
        main.py -> import Bus -> import Device -> import Bus -> ...
    We could really just don't use it, but with this we keep type declarations inside Bus class
    """
    # consts
    NAME_DEVICE_RAM     = 'Ram'
    NAME_DEVICE_CPU6502 = 'Cpu6502'

    def __init__(self, pc: c_uint16, sp: c_uint8, a: c_uint8, x: c_uint8, y: c_uint8, status: c_uint8,
                 fetched: c_uint8, addr_abs: c_uint16, addr_rel: c_uint16, opcode: c_uint8, cycles: c_uint8,
                 lookup: Dict[int, Any]):
        self.pc = pc
        self.sp = sp
        self.a = a
        self.x = x
        self.y = y
        self.status = status
        self.fetched = fetched
        self.addr_abs = addr_abs
        self.addr_rel = addr_rel
        self.opcode = opcode
        self.cycles = cycles
        self.lookup = lookup

    @abstractmethod
    def read(self, addr: c_uint16, *args, **kwargs) -> c_uint8:
        pass

    @abstractmethod
    def write(self, addr: c_uint16, data: c_uint8, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def fetch(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_flag(self, *args, **kwargs):
        pass

    @abstractmethod
    def set_flag(self, *args, **kwargs):
        pass
