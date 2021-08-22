from ctypes import c_uint8, c_uint16
from typing import Dict

from pynes.core.devices import AbstractDevice
from pynes.core.devices.cpu import address_modes as ams
from pynes.core.devices.cpu.instructions import opcode_instruction_mapping, instruction_by_opcode
from pynes.core.devices.cpu.utils import get_mask
from pynes.core.exceptions import NoSuchDeviceException


class Cpu6502(AbstractDevice):
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

        self.lookup = opcode_instruction_mapping(self)

    def reset(self) -> None:
        self.addr_abs.value = 0xfffc
        lo = self.read(c_uint16(self.addr_abs.value + 0))
        hi = self.read(c_uint16(self.addr_abs.value + 1))

        self.pc.value = (hi.value << 8) | lo.value

        self.a.value = self.x.value = self.y.value = 0
        self.sp.value = 0xfd
        self.status.value = 0x00 | get_mask('u')

        self.addr_rel.value = 0x0000
        self.addr_abs.value = 0x0000
        self.fetched.value = 0x00

        self.cycles.value = 8

    def clock(self) -> None:
        if self.cycles.value == 0:
            self.opcode.value = self.read(self.pc).value

            self.set_flag('u', True)

            self.pc.value += 1

            curr_inst = instruction_by_opcode(opcode=self.opcode.value,
                                              cpu=self)
            self.cycles.value = curr_inst.cycles.value

            add_cycle_1 = curr_inst.addr_mode(self)
            add_cycle_2 = curr_inst.operate()
            self.cycles.value += (add_cycle_1.value & add_cycle_2.value)

            self.set_flag('u', True)

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
        self.write(c_uint16(0x0100 + self.sp.value), c_uint8((self.pc.value >> 8) & 0x00ff))
        self.sp.value -= 1
        self.write(c_uint16(0x0100 + self.sp.value), c_uint8(self.pc.value & 0x00ff))
        self.sp.value -= 1

        self.set_flag('b', False)
        self.set_flag('u', True)
        self.set_flag('i', True)
        self.write(c_uint16(0x0100 + self.sp.value), self.status)
        self.sp.value -= 1

        self.addr_abs.value = 0xfffa
        lo = self.read(c_uint16(self.addr_abs.value + 0))
        hi = self.read(c_uint16(self.addr_abs.value + 1))
        self.pc.value = (hi.value << 8) | lo.value

        self.cycles.value = 8

    def complete(self) -> bool:
        return self.cycles.value == 0

    def disassemble(self, start, stop) -> Dict[int, str]:
        spaces_amt = 7
        ops_spaces_amt = 6
        map_lines = dict()
        addr = c_uint16(start)
        lo = c_uint8(0)
        hi = c_uint8(0)

        while addr.value <= stop:
            line_addr = addr.value
            # instruction addr
            instr_str = ('$' + hex(addr.value)[2:].zfill(4) + ':').ljust(spaces_amt)
            # instruction
            opcode = self.bus.address_owner(addr).read(addr, True).value
            instruction = instruction_by_opcode(opcode)
            addr.value += 1
            instr_str += instruction.name.ljust(ops_spaces_amt)
            # addressing mode
            # TODO: okay, I decided write a lot of if/elifs, but sure, there exists more
            #  elegant way to do it (Strategy maybe?)
            if instruction.addr_mode == ams.am_imp:
                instr_str += "{IMP}".ljust(ops_spaces_amt)
            elif instruction.addr_mode == ams.am_imm:
                value = self.bus.get_ram().read(addr, True)
                addr.value += 1
                instr_str += ("#$" + hex(value.value)[2:].zfill(2)).ljust(
                    ops_spaces_amt) + "{IMM}".ljust(ops_spaces_amt)
            elif instruction.addr_mode == ams.am_zp0:
                lo = self.bus.get_ram().read(addr, True)
                addr.value += 1
                hi.value = 0x00
                instr_str += ("$" + hex(lo.value)[2:].zfill(2) + ")").ljust(
                    ops_spaces_amt) + "{ZP0}".ljust(ops_spaces_amt)
            elif instruction.addr_mode == ams.am_zpx:
                lo = self.bus.get_ram().read(addr, True)
                addr.value += 1
                hi.value = 0x00
                instr_str += ("$" + hex(lo.value)[2:].zfill(2) + ", X)").ljust(
                    ops_spaces_amt) + "{ZPX}".ljust(ops_spaces_amt)
            elif instruction.addr_mode == ams.am_zpy:
                lo = self.bus.get_ram().read(addr, True)
                addr.value += 1
                hi.value = 0x00
                instr_str += ("$" + hex(lo.value)[2:].zfill(2) + ", Y)").ljust(
                    ops_spaces_amt) + "{ZPY}".ljust(ops_spaces_amt)
            elif instruction.addr_mode == ams.am_izx:
                lo = self.bus.get_ram().read(addr, True)
                addr.value += 1
                hi.value = 0x00
                instr_str += ("($" + hex(lo.value)[2:].zfill(2) + ", X)").ljust(
                    ops_spaces_amt) + "{IZX}".ljust(ops_spaces_amt)
            elif instruction.addr_mode == ams.am_izy:
                lo = self.bus.get_ram().read(addr, True)
                addr.value += 1
                hi.value = 0x00
                instr_str += ("($" + hex(lo.value)[2:].zfill(2) + ", Y)").ljust(
                    ops_spaces_amt) + "{IZY}".ljust(ops_spaces_amt)
            elif instruction.addr_mode == ams.am_abs:
                lo = self.bus.get_ram().read(addr, True)
                addr.value += 1
                hi = self.bus.get_ram().read(addr, True)
                addr.value += 1
                instr_str += ("$" + hex(c_uint16(
                    (hi.value << 8) | lo.value
                ).value)[2:].zfill(2)).ljust(ops_spaces_amt) + "{ABS}".ljust(ops_spaces_amt)
            elif instruction.addr_mode == ams.am_abx:
                lo = self.bus.get_ram().read(addr, True)
                addr.value += 1
                hi = self.bus.get_ram().read(addr, True)
                addr.value += 1
                instr_str += ("$" + hex(c_uint16(
                    (hi.value << 8) | lo.value
                ).value)[2:].zfill(2)).ljust(ops_spaces_amt) + ", X {ABX}".ljust(ops_spaces_amt)
            elif instruction.addr_mode == ams.am_aby:
                lo = self.bus.get_ram().read(addr, True)
                addr.value += 1
                hi = self.bus.get_ram().read(addr, True)
                addr.value += 1
                instr_str += ("$" + hex(c_uint16(
                    (hi.value << 8) | lo.value
                ).value)[2:].zfill(2)).ljust(ops_spaces_amt) + ", X {ABY}".ljust(ops_spaces_amt)
            elif instruction.addr_mode == ams.am_ind:
                lo = self.bus.get_ram().read(addr, True)
                addr.value += 1
                hi = self.bus.get_ram().read(addr, True)
                addr.value += 1
                instr_str += ("($" + hex(c_uint16(
                    (hi.value << 8) | lo.value
                ).value)[2:].zfill(2) + ")").ljust(ops_spaces_amt) + "{IND}".ljust(ops_spaces_amt)
            elif instruction.addr_mode == ams.am_rel:
                value = self.bus.get_ram().read(addr, True)
                addr.value += 1
                instr_str += ("$" + hex(value.value)[2:].zfill(2)).ljust(ops_spaces_amt) + ("[$" + hex(
                    addr.value + value.value
                )[2:].zfill(2) + "]").ljust(ops_spaces_amt) + " {REL}".ljust(ops_spaces_amt)
            # add to res
            map_lines.update({line_addr: instr_str})

        return map_lines

    def set_flag(self, flag: str, value: bool) -> None:
        mask = get_mask(flag)
        self.status.value = self.status.value | mask if value else self.status.value & ~mask

    def get_flag(self, flag: str) -> bool:
        mask = get_mask(flag)
        return (self.status.value & mask) > 0

    def read(self, addr: c_uint16) -> c_uint8:
        if not self.bus:
            raise NoSuchDeviceException()
        return self.bus.address_owner(addr).read(addr, False)

    def write(self, addr: c_uint16, data: c_uint8) -> None:
        if not self.bus:
            raise NoSuchDeviceException()
        self.bus.address_owner(addr).write(addr, data)

    def fetch(self) -> c_uint8:
        if not self.lookup.get(self.opcode.value).addr_mode == ams.am_imp:
            self.fetched.value = self.read(self.addr_abs).value
        return self.fetched
