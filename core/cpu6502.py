from ctypes import c_uint8, c_uint16, c_bool
from typing import Dict

import core.cpu6502_addr_modes as ams
from core.cpu6502_instructions import Cpu6502Instruction
from core.device.device import Device
from core.device.exceptions import NotConnectedToBusException


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
        self.fetched = c_uint8(0x00)
        self.addr_abs = c_uint16(0x0000)
        self.addr_rel = c_uint16(0x00)
        self.opcode = c_uint8(0x00)
        self.cycles = c_uint8(0)

        self.lookup = self.opcode_instruction_mapping()

    def reset(self) -> None:
        pass

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
        pass

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
