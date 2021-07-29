from ctypes import c_uint8, c_uint16, c_bool
from typing import Dict

import pynes.core.cpu6502_addr_modes as ams
from pynes.core.cpu6502_instructions import Cpu6502Instruction
from pynes.core.device.device import Device
from pynes.core.device.exceptions import NotConnectedToBusException


class Cpu6502(Device):
    INIT_VALUE_PC: int = 0x0000
    INIT_VALUE_SP: int = 0x00
    INIT_VALUE_REG: int = 0x00
    INIT_VALUE_STATUS: bool = False

    def __init__(self):
        super().__init__()
        # 6502 INTERNALS BEGIN
        self.pc = c_uint16(Cpu6502.INIT_VALUE_PC)  # program counter
        self.sp = c_uint8(Cpu6502.INIT_VALUE_SP)  # stack pointer
        # registers
        self.a = c_uint8(Cpu6502.INIT_VALUE_REG)  # accumulator
        self.x = c_uint8(Cpu6502.INIT_VALUE_REG)
        self.y = c_uint8(Cpu6502.INIT_VALUE_REG)
        self.status = c_uint8(0x00)
        # 6502 INTERNALS END
        self.fetched = c_uint8(0x00)
        self.addr_abs = c_uint16(0x0000)
        self.addr_rel = c_uint16(0x00)
        self.opcode = c_uint8(0x00)
        self.cycles = c_uint8(0)

        self.lookup = self.opcode_instruction_mapping()

    def set_flag(self, flag: str, value: bool) -> None:
        flags = ['c', 'z', 'i', 'd', 'b', 'u', 'v', 'n']
        shift_amt = flags.index(flag)
        mask = 1 << shift_amt
        self.status.value = self.status.value | mask if value else self.status.value & ~mask

    def get_flag(self, flag: str) -> bool:
        flags = ['c', 'z', 'i', 'd', 'b', 'u', 'v', 'n']
        shift_amt = flags.index(flag)
        mask = 1 << shift_amt
        return (self.status.value & mask) > 0

    def reset(self) -> None:
        self.a.value = self.x.value = self.y.value = 0
        self.sp.value = 0xfd
        self.status.value = 0x00 | (1 << 5)

        self.addr_abs.value = 0xfffc
        lo = self.read(c_uint16(self.addr_abs.value + 0))
        hi = self.read(c_uint16(self.addr_abs.value + 1))

        self.pc.value = (hi.value << 8) | lo.value

        self.addr_rel.value = 0x0000
        self.addr_abs.value = 0x0000
        self.fetched.value = 0x00

        self.cycles.value = 8

    def clock(self) -> None:
        if self.cycles.value == 0:
            self.opcode = self.read(self.pc)
            self.pc.value += 1
            curr_inst = self.lookup.get(self.opcode.value)

            self.cycles = curr_inst.cycles

            add_cycle_1 = curr_inst.addr_mode()
            add_cycle_2 = curr_inst.operate()

            self.cycles.value += (add_cycle_1.value & add_cycle_2.value)

        self.cycles.value -= 1

    def irq(self) -> None:
        if self.get_flag('i'):
            return
        self.write(c_uint16(0x0100 + self.sp.value), c_uint8((self.pc.value >> 8) & 0x00ff))
        self.sp.value -= 1
        self.write(c_uint16(0x0100 + self.sp.value), c_uint8(self.pc.value & 0x00ff))
        self.sp.value -= 1

        self.set_flag('b', False)
        self.set_flag('u', True)
        self.set_flag('i', True)
        self.write(c_uint16(0x0100 + self.sp.value), self.status)
        self.sp.value -= 1

        self.addr_abs.value = 0xfffc
        lo = self.read(c_uint16(self.addr_abs.value + 0))
        hi = self.read(c_uint16(self.addr_abs.value + 1))
        self.pc.value = (hi.value << 8) | lo.value

        self.cycles.value = 7

    def nmi(self) -> None:
        pass

    def fetch(self) -> c_uint8:
        if self.lookup.get(self.opcode.value).addr_mode == ams.am_imp:
            self.fetched = self.read(self.addr_abs)
        return self.fetched

    def read(self, addr: c_uint16) -> c_uint8:
        if not self.bus:
            raise NotConnectedToBusException()
        return self.bus.get_ram().read(addr, c_bool(False))

    def write(self, addr: c_uint16, data: c_uint8) -> None:
        if not self.bus:
            raise NotConnectedToBusException()
        self.bus.get_ram().write(addr, data)

    def opcode_instruction_mapping(self) -> Dict[int, Cpu6502Instruction]:
        mapping = dict()

        for instr_cls in Cpu6502Instruction.__subclasses__():
            foo = instr_cls.opcodes_mapping(self)
            mapping.update(foo)

        return mapping
