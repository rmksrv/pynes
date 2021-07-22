from ctypes import c_uint8, c_uint16, c_bool

from device import Device
from device_exceptions import NotConnectedToBusException


class Cpu6502(Device):

    INIT_VALUE_PC:     c_uint16 = c_uint16(0x0000)
    INIT_VALUE_SP:     c_uint8  = c_uint8(0x00)
    INIT_VALUE_REG:    c_uint8  = c_uint8(0x00)
    INIT_VALUE_STATUS: c_bool   = c_bool(False)

    def __init__(self):
        super().__init__()
        # 6502 INTERNALS BEGIN
        self.pc = Cpu6502.INIT_VALUE_PC  # program counter
        self.sp = Cpu6502.INIT_VALUE_SP  # stack pointer
        # registers
        self.a = Cpu6502.INIT_VALUE_REG  # accumulator
        self.x = Cpu6502.INIT_VALUE_REG
        self.y = Cpu6502.INIT_VALUE_REG
        # status flags
        self.c = Cpu6502.INIT_VALUE_STATUS  # carry flag
        self.z = Cpu6502.INIT_VALUE_STATUS  # zero
        self.i = Cpu6502.INIT_VALUE_STATUS  # disable interrupts
        self.d = Cpu6502.INIT_VALUE_STATUS  # decimal mode
        self.b = Cpu6502.INIT_VALUE_STATUS  # break
        self.u = Cpu6502.INIT_VALUE_STATUS  # unused
        self.v = Cpu6502.INIT_VALUE_STATUS  # overflow
        self.n = Cpu6502.INIT_VALUE_STATUS  # negative
        # 6502 INTERNALS END

    def read_from_ram(self, addr: c_uint16) -> c_uint8:
        if not self.bus:
            raise NotConnectedToBusException()
        return self.bus.get_ram().read(addr, c_bool(False))

    def write_to_ram(self, addr: c_uint16, data: c_uint8) -> None:
        if not self.bus:
            raise NotConnectedToBusException()
        self.bus.get_ram().write(addr, data)
