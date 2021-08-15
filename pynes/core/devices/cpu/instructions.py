from abc import ABC, abstractmethod
from ctypes import c_uint8, c_uint16
from typing import Callable, Dict, Optional, List

import pynes.core.devices.cpu.address_modes as address_modes
from pynes.core.devices.cpu.utils import get_mask


# http://www.obelisk.me.uk/6502/reference.html was used as instructions reference


# instruction template
class Cpu6502Instruction(ABC):

    def __init__(self, cpu, cycles: Optional[c_uint8],
                 addr_mode: Optional[Callable[[], c_uint8]]):
        self.cpu = cpu
        self.cycles = cycles
        self.addr_mode = addr_mode

    @property
    def name(self) -> str:
        return type(self).__name__

    @abstractmethod
    def operate(self) -> c_uint8:
        pass

    @staticmethod
    @abstractmethod
    def opcodes_mapping(cpu) -> Dict:
        pass


def opcode_instruction_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
    mapping = dict()

    for instr_cls in Cpu6502Instruction.__subclasses__():
        foo = instr_cls.opcodes_mapping(cpu)
        mapping.update(foo)

    return mapping


# instructions
class ADC(Cpu6502Instruction):
    """
    Add with Carry: This instruction adds the contents of a memory location to
    the accumulator together with the carry bit. If overflow occurs the carry bit
    is set, this enables multiple byte addition to be performed.
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()
        tmp = c_uint16(self.cpu.a.value + self.cpu.fetched.value + int(self.cpu.get_flag('c')))

        self.cpu.set_flag('c', tmp.value > 0xff)
        self.cpu.set_flag('z', (tmp.value & 0xff) == 0)
        self.cpu.set_flag('n', bool(tmp.value & 0x80))
        self.cpu.set_flag('v', bool(
            (~(self.cpu.a.value ^ self.cpu.fetched.value) & (self.cpu.a.value ^ tmp.value)) & 0x0080
        ))

        self.cpu.a.value = tmp.value & 0x00ff
        return c_uint8(1)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x69: ADC(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0x65: ADC(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0x75: ADC(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_zpx),
            0x6d: ADC(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
            0x7d: ADC(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abx),
            0x79: ADC(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_aby),
            0x61: ADC(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_izx),
            0x71: ADC(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_izy),
        }


class AND(Cpu6502Instruction):
    """
    Logical AND: performed bit by bit on acc value with fetched from memory byte
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()
        self.cpu.a.value &= self.cpu.fetched.value

        self.cpu.set_flag('z', self.cpu.a.value == 0x00)
        self.cpu.set_flag('n', bool(self.cpu.a.value & 0x80))
        return c_uint8(1)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x29: AND(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0x25: AND(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0x32: AND(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_zpx),
            0x2d: AND(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
            0x3d: AND(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abx),
            0x39: AND(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_aby),
            0x21: AND(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_izx),
            0x31: AND(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_izy),
        }


class ASL(Cpu6502Instruction):
    """
    Arithmetic Shift Left: This operation shifts all the bits of the accumulator or memory contents one
    bit left. Bit 0 is set to 0 and bit 7 is placed in the carry flag. The effect of this operation is
    to multiply the memory contents by 2 (ignoring 2's complement considerations), setting the carry
    if the result will not fit in 8 bits.
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()
        tmp = c_uint16(self.cpu.fetched.value << 1)

        self.cpu.set_flag('c', (tmp.value & 0xff00) > 0)
        self.cpu.set_flag('z', (tmp.value & 0xff) == 0)
        self.cpu.set_flag('n', bool(tmp.value & 0x80))

        result = c_uint8(tmp.value & 0x00ff)
        if self.cpu.lookup[self.cpu.opcode.value].addr_mode == address_modes.am_imp:
            self.cpu.a.value = result.value
        else:
            self.cpu.write(self.cpu.addr_abs, result)

        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x0a: ASL(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp),
            0x06: ASL(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_zp0),
            0x16: ASL(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_zpx),
            0x0e: ASL(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_abs),
            0x1e: ASL(cpu, cycles=c_uint8(7), addr_mode=address_modes.am_abx),
        }


class BCC(Cpu6502Instruction):
    """
    Branch if Carry Clear: if C not set then add relative address to PC to cause a branch to new location
    """

    def operate(self) -> c_uint8:
        if not self.cpu.get_flag('c'):
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x90: BCC(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_rel)
        }


class BCS(Cpu6502Instruction):
    """
    Branch if Carry Set: if C set then add relative address to PC to cause a branch to new location
    """

    def operate(self) -> c_uint8:
        if self.cpu.get_flag('c'):
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xb0: BCS(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_rel)
        }


class BEQ(Cpu6502Instruction):
    """
    Branch if Equal: If the zero flag is set then add the relative displacement
    to the program counter to cause a branch to a new location.
    """

    def operate(self) -> c_uint8:
        if self.cpu.get_flag('z'):
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xf0: BEQ(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_rel)
        }


class BIT(Cpu6502Instruction):
    """
    Bit Test: This instructions is used to test if one or more bits are set in a target
    memory location. The mask pattern in A is ANDed with the value in memory to set or
    clear the zero flag, but the result is not kept. Bits 7 and 6 of the value from
    memory are copied into the N and V flags.
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()
        tmp = self.cpu.a.value & self.cpu.fetched.value

        self.cpu.set_flag('z', (tmp & 0xff) == 0)
        self.cpu.set_flag('n', bool(self.cpu.fetched.value & (1 << 7)))
        self.cpu.set_flag('v', bool(self.cpu.fetched.value & (1 << 6)))

        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x24: BIT(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0x2c: BIT(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
        }


class BMI(Cpu6502Instruction):
    """
    Branch if Minus: If the negative flag is set then add the relative displacement
    to the program counter to cause a branch to a new location.
    """

    def operate(self) -> c_uint8:
        if self.cpu.get_flag('n'):
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x30: BMI(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_rel)
        }


class BNE(Cpu6502Instruction):
    """
    Branch if Not Equal: If the zero flag is clear then add the relative displacement
    to the program counter to cause a branch to a new location.
    """

    def operate(self) -> c_uint8:
        if not self.cpu.get_flag('z'):
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xd0: BNE(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_rel)
        }


class BPL(Cpu6502Instruction):
    """
    Branch if Positive: If the negative flag is clear then add the relative displacement
    to the program counter to cause a branch to a new location.
    """

    def operate(self) -> c_uint8:
        if not self.cpu.get_flag('n'):
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x10: BPL(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_rel)
        }


class BRK(Cpu6502Instruction):
    """
    Force Interrupt: The BRK instruction forces the generation of an interrupt request.
    The program counter and processor status are pushed on the stack then the IRQ interrupt
    vector at $FFFE/F is loaded into the PC and the break flag in the status set to one.
    """

    def operate(self) -> c_uint8:
        self.cpu.pc.value += 1

        self.cpu.set_flag('i', True)
        self.cpu.write(c_uint16(0x0100 + self.cpu.sp.value),
                       c_uint8((self.cpu.pc.value >> 8) & 0x00ff))
        self.cpu.sp.value -= 1
        self.cpu.write(c_uint16(0x0100 + self.cpu.sp.value),
                       c_uint8(self.cpu.pc.value & 0x00ff))
        self.cpu.sp.value -= 1

        self.cpu.set_flag('b', True)
        self.cpu.write(c_uint16(0x0100 + self.cpu.sp.value), self.cpu.status)
        self.cpu.sp.value -= 1
        self.cpu.set_flag('b', False)

        self.cpu.pc.value = c_uint16(
            self.cpu.read(c_uint16(0xfffe)).value | (self.cpu.read(c_uint16(0xffff)).value << 8)
        ).value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x00: BRK(cpu, cycles=c_uint8(7), addr_mode=address_modes.am_imp)
        }


class BVC(Cpu6502Instruction):
    """
    Branch if Overflow Clear: If the overflow flag is clear then add the relative displacement
    to the program counter to cause a branch to a new location.
    """

    def operate(self) -> c_uint8:
        if not self.cpu.get_flag('v'):
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x50: BVC(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_rel)
        }


class BVS(Cpu6502Instruction):
    """
    Branch if Overflow Set: If the overflow flag is set then add the relative displacement
    to the program counter to cause a branch to a new location.
    """

    def operate(self) -> c_uint8:
        if self.cpu.get_flag('v'):
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x70: BVS(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_rel)
        }


class CLC(Cpu6502Instruction):
    """
    Clear Carry Flag: Set the carry flag to zero.
    """

    def operate(self) -> c_uint8:
        self.cpu.set_flag('c', False)
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x18: CLC(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class CLD(Cpu6502Instruction):
    """
    Clear Decimal Mode: Sets the decimal mode flag to zero.
    """

    def operate(self) -> c_uint8:
        self.cpu.set_flag('d', False)
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xd8: CLD(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class CLI(Cpu6502Instruction):
    """
    Clear Interrupt Disable: Clears the interrupt disable flag allowing normal
    interrupt requests to be serviced.
    """

    def operate(self) -> c_uint8:
        self.cpu.set_flag('i', False)
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x58: CLI(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class CLV(Cpu6502Instruction):
    """
    Clear Overflow Flag: Clears the overflow flag.
    """

    def operate(self) -> c_uint8:
        self.cpu.set_flag('v', False)
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xb8: CLV(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class CMP(Cpu6502Instruction):
    """
    Compare: This instruction compares the contents of the accumulator with another memory
    held value and sets the zero and carry flags as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()
        tmp = self.cpu.a.value - self.cpu.fetched.value

        self.cpu.set_flag('c', self.cpu.a.value >= self.cpu.fetched.value)
        self.cpu.set_flag('z', (tmp & 0xff) == 0x00)
        self.cpu.set_flag('n', bool(tmp & 0x80))

        return c_uint8(1)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xc9: CMP(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0xc5: CMP(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0xd5: CMP(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_zpx),
            0xcd: CMP(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
            0xdd: CMP(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abx),
            0xd9: CMP(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_aby),
            0xc1: CMP(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_izx),
            0xd1: CMP(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_izy),
        }


class CPX(Cpu6502Instruction):
    """
    Compare X Register: This instruction compares the contents of the X register with another
    memory held value and sets the zero and carry flags as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()
        tmp = self.cpu.x.value - self.cpu.fetched.value

        self.cpu.set_flag('c', self.cpu.x.value >= self.cpu.fetched.value)
        self.cpu.set_flag('z', (tmp & 0xff) == 0x00)
        self.cpu.set_flag('n', bool(tmp & 0x80))

        return c_uint8(1)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xe0: CPX(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0xe4: CPX(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0xec: CPX(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
        }


class CPY(Cpu6502Instruction):
    """
    Compare Y Register: This instruction compares the contents of the Y register with another
    memory held value and sets the zero and carry flags as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()
        tmp = self.cpu.y.value - self.cpu.fetched.value

        self.cpu.set_flag('c', self.cpu.y.value >= self.cpu.fetched.value)
        self.cpu.set_flag('z', (tmp & 0xff) == 0x00)
        self.cpu.set_flag('n', bool(tmp & 0x80))

        return c_uint8(1)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xc0: CPY(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0xc4: CPY(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0xcc: CPY(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
        }


class DEC(Cpu6502Instruction):
    """
    Decrement Memory: Subtracts one from the value held at a specified memory location setting
    the zero and negative flags as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()

        tmp = self.cpu.fetched.value - 1
        self.cpu.write(self.cpu.addr_abs, c_uint8(tmp))
        self.cpu.set_flag('z', (tmp & 0xff) == 0)
        self.cpu.set_flag('n', bool(tmp & 0x80))

        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xc6: DEC(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_zp0),
            0xd6: DEC(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_zpx),
            0xce: DEC(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_abs),
            0xde: DEC(cpu, cycles=c_uint8(7), addr_mode=address_modes.am_abx),
        }


class DEX(Cpu6502Instruction):
    """
    Decrement X Register: Subtracts one from the X register setting the zero and negative
    flags as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.x.value -= 1
        self.cpu.set_flag('z', (self.cpu.x.value & 0xff) == 0)
        self.cpu.set_flag('n', bool(self.cpu.x.value & 0x80))
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xca: DEX(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class DEY(Cpu6502Instruction):
    """
    Decrement Y Register: Subtracts one from the Y register setting the zero and negative
    flags as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.y.value -= 1
        self.cpu.set_flag('z', (self.cpu.y.value & 0xff) == 0)
        self.cpu.set_flag('n', bool(self.cpu.y.value & 0x80))
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x88: DEY(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class EOR(Cpu6502Instruction):
    """
    Exclusive OR: An exclusive OR is performed, bit by bit, on the accumulator contents
    using the contents of a byte of memory.
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()
        self.cpu.a.value ^= self.cpu.fetched.value

        self.cpu.set_flag('z', self.cpu.a.value == 0x00)
        self.cpu.set_flag('n', bool(self.cpu.a.value & 0x80))
        return c_uint8(1)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x49: EOR(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0x45: EOR(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0x55: EOR(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_zpx),
            0x4d: EOR(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
            0x5d: EOR(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abx),
            0x59: EOR(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_aby),
            0x41: EOR(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_izx),
            0x51: EOR(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_izy),
        }


class INC(Cpu6502Instruction):
    """
    Increment Memory: Adds one to the value held at a specified memory location setting
    the zero and negative flags as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()

        tmp = self.cpu.fetched.value + 1
        self.cpu.write(self.cpu.addr_abs, c_uint8(tmp))
        self.cpu.set_flag('z', (tmp & 0xff) == 0)
        self.cpu.set_flag('n', bool(tmp & 0x80))
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xe6: INC(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_zp0),
            0xf6: INC(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_zpx),
            0xee: INC(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_abs),
            0xfe: INC(cpu, cycles=c_uint8(7), addr_mode=address_modes.am_abx),
        }


class INX(Cpu6502Instruction):
    """
    Increment X Register: Adds one to the X register setting the zero and negative flags
    as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.x.value += 1
        self.cpu.set_flag('z', (self.cpu.x.value & 0xff) == 0)
        self.cpu.set_flag('n', bool(self.cpu.x.value & 0x80))
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xe8: INX(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class INY(Cpu6502Instruction):
    """
    Increment Y Register: Adds one to the Y register setting the zero and negative flags
    as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.y.value += 1
        self.cpu.set_flag('z', (self.cpu.y.value & 0xff) == 0)
        self.cpu.set_flag('n', bool(self.cpu.y.value & 0x80))
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xc8: INY(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class JMP(Cpu6502Instruction):
    """
    Jump: Sets the program counter to the address specified by the operand.
    NOTE:
    An original 6502 has does not correctly fetch the target address if the indirect vector
    falls on a page boundary (e.g. $xxFF where xx is any value from $00 to $FF). In this case
    fetches the LSB from $xxFF as expected but takes the MSB from $xx00. This is fixed in
    some later chips like the 65SC02 so for compatibility always ensure the indirect vector
    is not at the end of the page.
    """

    def operate(self) -> c_uint8:
        self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x4c: JMP(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_abs),
            0x6c: JMP(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_ind),
        }


class JSR(Cpu6502Instruction):
    """
    Jump to Subroutine: The JSR instruction pushes the address (minus one) of the return
    point on to the stack and then sets the program counter to the target memory address.
    """

    def operate(self) -> c_uint8:
        self.cpu.pc.value -= 1

        self.cpu.write(c_uint16(0x0100 + self.cpu.sp.value),
                       c_uint8((self.cpu.pc.value >> 8) & 0x00ff))
        self.cpu.sp.value -= 1
        self.cpu.write(c_uint16(0x0100 + self.cpu.sp.value),
                       c_uint8(self.cpu.pc.value & 0x00ff))
        self.cpu.sp.value -= 1

        self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x20: JSR(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_abs),
        }


class LDA(Cpu6502Instruction):
    """
    Load Accumulator: Loads a byte of memory into the accumulator setting the zero and
    negative flags as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.a.value = self.cpu.fetch().value
        self.cpu.set_flag('z', self.cpu.a.value == 0)
        self.cpu.set_flag('n', bool(self.cpu.a.value & 0x80))
        return c_uint8(1)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xa9: LDA(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0xa5: LDA(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0xb5: LDA(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_zpx),
            0xad: LDA(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
            0xbd: LDA(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abx),
            0xb9: LDA(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_aby),
            0xa1: LDA(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_izx),
            0xb1: LDA(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_izy),
        }


class LDX(Cpu6502Instruction):
    """
    Load X Register: Loads a byte of memory into the X register setting the zero
    and negative flags as appropriate.
    """

    def operate(self) -> c_uint8:
        # self.cpu.x.value = self.cpu.fetch().value
        self.cpu.fetch()
        self.cpu.x.value = self.cpu.fetched.value
        self.cpu.set_flag('z', self.cpu.x.value == 0)
        self.cpu.set_flag('n', bool(self.cpu.x.value & 0x80))
        return c_uint8(1)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xa2: LDX(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0xa6: LDX(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0xb6: LDX(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_zpy),
            0xae: LDX(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
            0xbe: LDX(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_aby),
        }


class LDY(Cpu6502Instruction):
    """
    Load Y Register: Loads a byte of memory into the Y register setting the zero
    and negative flags as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.y.value = self.cpu.fetch().value
        self.cpu.set_flag('z', self.cpu.y.value == 0)
        self.cpu.set_flag('n', bool(self.cpu.y.value & 0x80))
        return c_uint8(1)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xa0: LDY(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0xa4: LDY(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0xb4: LDY(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_zpx),
            0xac: LDY(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
            0xbc: LDY(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abx),
        }


class LSR(Cpu6502Instruction):
    """
    Logical Shift Right: Each of the bits in A or M is shift one place to the right.
    The bit that was in bit 0 is shifted into the carry flag. Bit 7 is set to zero.
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()
        self.cpu.set_flag('c', bool(self.cpu.fetched.value & 0x0001))
        tmp = c_uint16(self.cpu.fetched.value >> 1)
        self.cpu.set_flag('z', (tmp.value & 0xff) == 0)
        self.cpu.set_flag('n', bool(tmp.value & 0x80))
        result = c_uint8(tmp.value & 0x00ff)

        if self.cpu.lookup[self.cpu.opcode.value].addr_mode == address_modes.am_imp:
            self.cpu.a.value = result.value
        else:
            self.cpu.write(self.cpu.addr_abs, result)

        return c_uint8(1)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x4a: LSR(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0x46: LSR(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_zp0),
            0x56: LSR(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_zpx),
            0x4e: LSR(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_abs),
            0x5e: LSR(cpu, cycles=c_uint8(7), addr_mode=address_modes.am_abx),
        }


class NOP(Cpu6502Instruction):
    """
    No Operation: The NOP instruction causes no changes to the processor other
    than the normal incrementing of the program counter to the next instruction.
    """

    def operate(self) -> c_uint8:
        return c_uint8(1) if self.cpu.opcode.value in NOP.illegal_opcodes() else c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xea: NOP(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }

    @staticmethod
    def illegal_opcodes() -> List[int]:
        return [0x1c, 0x3c, 0x5c, 0x7c, 0xdc, 0xfc]


class ORA(Cpu6502Instruction):
    """
    Logical Inclusive OR: An inclusive OR is performed, bit by bit, on the
    accumulator contents using the contents of a byte of memory.
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()
        self.cpu.a.value |= self.cpu.fetched.value
        self.cpu.set_flag('z', self.cpu.a.value == 0)
        self.cpu.set_flag('n', bool(self.cpu.a.value & 0x80))
        return c_uint8(1)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x09: ORA(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0x05: ORA(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0x15: ORA(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_zpx),
            0x0d: ORA(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
            0x1d: ORA(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abx),
            0x19: ORA(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_aby),
            0x01: ORA(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_izx),
            0x11: ORA(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_izy),
        }


class PHA(Cpu6502Instruction):
    """
    Push Accumulator: Pushes a copy of the accumulator on to the stack.
    """

    def operate(self) -> c_uint8:
        self.cpu.write(c_uint16(0x0100 + self.cpu.sp.value), self.cpu.a)
        self.cpu.sp.value -= 1
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x48: PHA(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_imp)
        }


class PHP(Cpu6502Instruction):
    """
    Push Processor Status: Pushes a copy of the status flags on to the stack.
    """

    def operate(self) -> c_uint8:
        b = get_mask('b')
        u = get_mask('u')
        self.cpu.write(c_uint16(0x0100 + self.cpu.sp.value), c_uint8(self.cpu.status.value | b | u))
        self.cpu.set_flag('b', False)
        self.cpu.set_flag('u', False)
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x08: PHP(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_imp)
        }


class PLA(Cpu6502Instruction):
    """
    Pull Accumulator: Pulls an 8 bit value from the stack and into the accumulator.
    The zero and negative flags are set as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.sp.value += 1
        self.cpu.a.value = self.cpu.read(c_uint16(0x0100 + self.cpu.sp.value)).value
        self.cpu.set_flag('z', self.cpu.a.value == 0x00)
        self.cpu.set_flag('n', bool(self.cpu.a.value & 0x80))
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x68: PLA(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_imp)
        }


class PLP(Cpu6502Instruction):
    """
    Pull Processor Status: Pulls an 8 bit value from the stack and into the processor
    flags. The flags will take on new states as determined by the value pulled.
    """

    def operate(self) -> c_uint8:
        self.cpu.sp.value += 1
        self.cpu.status.value = self.cpu.read(c_uint16(0x0100 + self.cpu.sp.value))
        self.cpu.set_flag('u', True)
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x28: PLP(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_imp)
        }


class ROL(Cpu6502Instruction):
    """
    Rotate Left: Move each of the bits in either A or M one place to the left.
    Bit 0 is filled with the current value of the carry flag whilst the old bit 7
    becomes the new carry flag value.
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()
        tmp = c_uint16((self.cpu.fetched.value << 1) | self.cpu.get_flag('c'))

        self.cpu.set_flag('c', tmp.value & 0xff00)
        self.cpu.set_flag('z', (tmp.value & 0xff) == 0)
        self.cpu.set_flag('n', bool(tmp.value & 0x80))

        result = c_uint8(tmp.value & 0x00ff)
        if self.cpu.lookup[self.cpu.opcode.value].addr_mode == address_modes.am_imp:
            self.cpu.a.value = result.value
        else:
            self.cpu.write(self.cpu.addr_abs, result)

        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x2a: ROL(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0x26: ROL(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_zp0),
            0x36: ROL(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_zpx),
            0x2e: ROL(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_abs),
            0x3e: ROL(cpu, cycles=c_uint8(7), addr_mode=address_modes.am_abx),
        }


class ROR(Cpu6502Instruction):
    """
    Rotate Right: Move each of the bits in either A or M one place to the right. Bit 7
    is filled with the current value of the carry flag whilst the old bit 0 becomes the
    new carry flag value.
    """

    def operate(self):
        self.cpu.fetch()
        tmp = c_uint16((self.cpu.get_flag('c') << 7) | (self.cpu.fetched.value >> 1))

        self.cpu.set_flag('c', self.cpu.fetched.value & 0x01)
        self.cpu.set_flag('z', (tmp.value & 0xff) == 0)
        self.cpu.set_flag('n', bool(tmp.value & 0x80))

        result = c_uint8(tmp.value & 0x00ff)
        if self.cpu.lookup[self.cpu.opcode.value].addr_mode == address_modes.am_imp:
            self.cpu.a.value = result.value
        else:
            self.cpu.write(self.cpu.addr_abs, result)

        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x6a: ROR(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0x66: ROR(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_zp0),
            0x76: ROR(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_zpx),
            0x6e: ROR(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_abs),
            0x7e: ROR(cpu, cycles=c_uint8(7), addr_mode=address_modes.am_abx),
        }


class RTI(Cpu6502Instruction):
    """
    Return from Interrupt: The RTI instruction is used at the end of an interrupt processing routine.
    It pulls the processor flags from the stack followed by the program counter.
    """

    def operate(self) -> c_uint8:
        self.cpu.sp.value += 1
        self.cpu.status.value = self.cpu.read(c_uint16(0x0100 + self.cpu.sp.value)).value
        self.cpu.status.value &= ~self.cpu.get_flag('b')
        self.cpu.status.value &= ~self.cpu.get_flag('u')

        self.cpu.sp.value += 1
        self.cpu.pc.value = self.cpu.read(c_uint16(0x0100 + self.cpu.sp.value)).value
        self.cpu.sp.value += 1
        self.cpu.pc.value |= self.cpu.read(c_uint16((0x0100 + self.cpu.sp.value) << 8)).value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x40: RTI(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_imp)
        }


class RTS(Cpu6502Instruction):
    """
    Return from Subroutine: The RTS instruction is used at the end of a subroutine
    to return to the calling routine. It pulls the program counter (minus one) from
    the stack.
    """

    def operate(self) -> c_uint8:
        self.cpu.sp.value += 1
        self.cpu.pc.value = self.cpu.read(c_uint16(0x0100 + self.cpu.sp.value)).value
        self.cpu.sp.value += 1
        self.cpu.pc.value |= self.cpu.read(c_uint16((0x0100 + self.cpu.sp.value) << 8)).value
        self.cpu.pc.value += 1
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x60: RTS(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_imp)
        }


class SBC(Cpu6502Instruction):
    """
    Subtract with Carry: This instruction subtracts the contents of a memory location
    to the accumulator together with the not of the carry bit. If overflow occurs the
    carry bit is clear, this enables multiple byte subtraction to be performed.
    """

    def operate(self) -> c_uint8:
        self.cpu.fetch()
        neg_fetch = c_uint16(self.cpu.fetched.value ^ 0x00ff)
        tmp = c_uint16(self.cpu.a.value + neg_fetch.value + int(self.cpu.get_flag('c')))

        self.cpu.set_flag('c', tmp.value > 0xff)
        self.cpu.set_flag('z', (tmp.value & 0xff) == 0)
        self.cpu.set_flag('n', bool(tmp.value & 0x80))
        self.cpu.set_flag('v', bool((self.cpu.a.value ^ neg_fetch.value) & (self.cpu.a.value ^ tmp.value) & 0x0080))

        self.cpu.a.value = tmp.value & 0x00ff
        return c_uint8(1)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xe9: SBC(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imm),
            0xe5: SBC(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0xf5: SBC(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_zpx),
            0xed: SBC(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
            0xfd: SBC(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abx),
            0xf9: SBC(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_aby),
            0xe1: SBC(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_izx),
            0xf1: SBC(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_izy),
        }


class SEC(Cpu6502Instruction):
    """
    Set Carry Flag: Set the carry flag to one.
    """

    def operate(self) -> c_uint8:
        # self.cpu.c.value = True
        self.cpu.set_flag('c', True)
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x38: SEC(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class SED(Cpu6502Instruction):
    """
    Set Decimal Flag: Set the decimal mode flag to one.
    """

    def operate(self) -> c_uint8:
        self.cpu.set_flag('d', True)
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xf8: SED(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class SEI(Cpu6502Instruction):
    """
    Set Interrupt Disable: Set the interrupt disable flag to one.
    """

    def operate(self) -> c_uint8:
        self.cpu.set_flag('i', True)
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x78: SEI(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class STA(Cpu6502Instruction):
    """
    Store Accumulator: Stores the contents of the accumulator into memory.
    """

    def operate(self) -> c_uint8:
        self.cpu.write(self.cpu.addr_abs, self.cpu.a)
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x85: STA(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0x95: STA(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_zpx),
            0x8d: STA(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
            0x9d: STA(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_abx),
            0x99: STA(cpu, cycles=c_uint8(5), addr_mode=address_modes.am_aby),
            0x81: STA(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_izx),
            0x91: STA(cpu, cycles=c_uint8(6), addr_mode=address_modes.am_izy),
        }


class STX(Cpu6502Instruction):
    """
    Store X Register: Stores the contents of the X register into memory.
    """

    def operate(self) -> c_uint8:
        self.cpu.write(self.cpu.addr_abs, self.cpu.x)
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x86: STX(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0x96: STX(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_zpy),
            0x8e: STX(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
        }


class STY(Cpu6502Instruction):
    """
    Store Y Register: Stores the contents of the Y register into memory.
    """

    def operate(self) -> c_uint8:
        self.cpu.write(self.cpu.addr_abs, self.cpu.y)
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x84: STY(cpu, cycles=c_uint8(3), addr_mode=address_modes.am_zp0),
            0x94: STY(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_zpx),
            0x8c: STY(cpu, cycles=c_uint8(4), addr_mode=address_modes.am_abs),
        }


class TAX(Cpu6502Instruction):
    """
    Transfer Accumulator to X: Copies the current contents of the accumulator
    into the X register and sets the zero and negative flags as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.x.value = self.cpu.a.value
        self.cpu.set_flag('z', self.cpu.x.value == 0)
        self.cpu.set_flag('n', bool(self.cpu.x.value & 0x80))
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xaa: TAX(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class TAY(Cpu6502Instruction):
    """
    Transfer Accumulator to Y: Copies the current contents of the accumulator
    into the Y register and sets the zero and negative flags as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.y.value = self.cpu.a.value
        self.cpu.set_flag('z', self.cpu.y.value == 0)
        self.cpu.set_flag('n', bool(self.cpu.y.value & 0x80))
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xa8: TAY(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class TSX(Cpu6502Instruction):
    """
    Transfer Stack Pointer to X: Copies the current contents of the stack
    register into the X register and sets the zero and negative flags as
    appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.x.value = self.cpu.sp.value
        self.cpu.set_flag('z', self.cpu.x.value == 0)
        self.cpu.set_flag('n', bool(self.cpu.x.value & 0x80))
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0xba: TSX(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class TXA(Cpu6502Instruction):
    """
    Transfer X to Accumulator: Copies the current contents of the X register
    into the accumulator and sets the zero and negative flags as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.a.value = self.cpu.x.value
        self.cpu.set_flag('z', self.cpu.a.value == 0)
        self.cpu.set_flag('n', bool(self.cpu.a.value & 0x80))
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x8a: TXA(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class TXS(Cpu6502Instruction):
    """
    Transfer X to Stack Pointer: Copies the current contents of the X register
    into the stack register.
    """

    def operate(self) -> c_uint8:
        self.cpu.sp.value = self.cpu.x.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x9a: TXS(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class TYA(Cpu6502Instruction):
    """
    Transfer Y to Accumulator: Copies the current contents of the Y register
    into the accumulator and sets the zero and negative flags as appropriate.
    """

    def operate(self) -> c_uint8:
        self.cpu.a.value = self.cpu.y.value
        self.cpu.set_flag('z', self.cpu.a.value == 0)
        self.cpu.set_flag('n', bool(self.cpu.a.value & 0x80))
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {
            0x98: TYA(cpu, cycles=c_uint8(2), addr_mode=address_modes.am_imp)
        }


class XXX(Cpu6502Instruction):
    """
    For illegal opcodes
    """

    def operate(self) -> c_uint8:
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu) -> Dict[int, Cpu6502Instruction]:
        return {}


def instruction_by_opcode(opcode: int, cpu=None) -> Cpu6502Instruction:
    return opcode_instruction_mapping(cpu).get(opcode, XXX(cpu, cycles=c_uint8(0), addr_mode=address_modes.am_imp))
