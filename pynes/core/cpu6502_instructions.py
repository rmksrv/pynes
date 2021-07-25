from abc import ABC, abstractmethod
from ctypes import c_uint8
from dataclasses import dataclass
from typing import Callable, Dict

import pynes.core.cpu6502_addr_modes as ams
from pynes.core.device.fake_device import FakeDevice


# http://www.obelisk.me.uk/6502/reference.html was used as instructions reference

# instruction template
@dataclass
class Cpu6502Instruction(ABC):
    cpu:       FakeDevice
    cycles:    c_uint8
    addr_mode: Callable[[], c_uint8]

    @property
    def name(self) -> str:
        return type(self).__name__

    @abstractmethod
    def operate(self) -> c_uint8:
        pass

    @staticmethod
    @abstractmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict:
        pass


class ADC(Cpu6502Instruction):
    def operate(self) -> c_uint8:
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x69: ADC(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0x65: ADC(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0x75: ADC(cpu, cycles=c_uint8(4), addr_mode=ams.am_zpx),
            0x6d: ADC(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
            0x7d: ADC(cpu, cycles=c_uint8(4), addr_mode=ams.am_abx),
            0x79: ADC(cpu, cycles=c_uint8(4), addr_mode=ams.am_aby),
            0x61: ADC(cpu, cycles=c_uint8(6), addr_mode=ams.am_izx),
            0x71: ADC(cpu, cycles=c_uint8(5), addr_mode=ams.am_izy),
        }


class AND(Cpu6502Instruction):
    """
    Logical AND: performed bit by bit on acc value with fetched from memory byte
    """
    def operate(self) -> c_uint8:
        self.cpu.fetch()
        self.cpu.a.value &= self.cpu.fetched.value
        self.cpu.z.value = (self.cpu.a.value == 0x00)
        self.cpu.n.value = (self.cpu.a.value & 0x80)
        return c_uint8(1)

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x29: AND(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0x25: AND(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0x32: AND(cpu, cycles=c_uint8(4), addr_mode=ams.am_zpx),
            0x2d: AND(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
            0x3d: AND(cpu, cycles=c_uint8(4), addr_mode=ams.am_abx),
            0x39: AND(cpu, cycles=c_uint8(4), addr_mode=ams.am_aby),
            0x21: AND(cpu, cycles=c_uint8(6), addr_mode=ams.am_izx),
            0x31: AND(cpu, cycles=c_uint8(5), addr_mode=ams.am_izy),
        }


class ASL(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x0a: ASL(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp),
            0x06: ASL(cpu, cycles=c_uint8(5), addr_mode=ams.am_zp0),
            0x16: ASL(cpu, cycles=c_uint8(6), addr_mode=ams.am_zpx),
            0x0e: ASL(cpu, cycles=c_uint8(6), addr_mode=ams.am_abs),
            0x1e: ASL(cpu, cycles=c_uint8(7), addr_mode=ams.am_abx),
        }


class BCC(Cpu6502Instruction):
    """
    Branch if Carry Clear: if C not set then add relative address to PC to cause a branch to new location
    """
    def operate(self):
        if not self.cpu.c.value:
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x90: BCC(cpu, cycles=c_uint8(2), addr_mode=ams.am_rel)
        }


class BCS(Cpu6502Instruction):
    """
    Branch if Carry Set: if C set then add relative address to PC to cause a branch to new location
    """
    def operate(self) -> c_uint8:
        if self.cpu.c.value:
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xb0: BCS(cpu, cycles=c_uint8(2), addr_mode=ams.am_rel)
        }


class BEQ(Cpu6502Instruction):
    """
    Branch if Equal: If the zero flag is set then add the relative displacement
    to the program counter to cause a branch to a new location.
    """
    def operate(self):
        if self.cpu.z.value:
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xf0: BEQ(cpu, cycles=c_uint8(2), addr_mode=ams.am_rel)
        }


class BIT(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x24: BIT(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0x2c: BIT(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
        }


class BMI(Cpu6502Instruction):
    """
    Branch if Minus: If the negative flag is set then add the relative displacement
    to the program counter to cause a branch to a new location.
    """
    def operate(self):
        if self.cpu.n.value:
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x30: BMI(cpu, cycles=c_uint8(2), addr_mode=ams.am_rel)
        }


class BNE(Cpu6502Instruction):
    """
    Branch if Not Equal: If the zero flag is clear then add the relative displacement
    to the program counter to cause a branch to a new location.
    """
    def operate(self):
        if not self.cpu.z.value:
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xd0: BNE(cpu, cycles=c_uint8(2), addr_mode=ams.am_rel)
        }


class BPL(Cpu6502Instruction):
    """
    Branch if Positive: If the negative flag is clear then add the relative displacement
    to the program counter to cause a branch to a new location.
    """
    def operate(self):
        if not self.cpu.n.value:
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x10: BPL(cpu, cycles=c_uint8(2), addr_mode=ams.am_rel)
        }


class BRK(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x00: BRK(cpu, cycles=c_uint8(7), addr_mode=ams.am_imp)
        }


class BVC(Cpu6502Instruction):
    """
    Branch if Overflow Clear: If the overflow flag is clear then add the relative displacement
    to the program counter to cause a branch to a new location.
    """
    def operate(self):
        if not self.cpu.v.value:
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x50: BVC(cpu, cycles=c_uint8(2), addr_mode=ams.am_rel)
        }


class BVS(Cpu6502Instruction):
    """
    Branch if Overflow Set: If the overflow flag is set then add the relative displacement
    to the program counter to cause a branch to a new location.
    """
    def operate(self):
        if self.cpu.v.value:
            self.cpu.cycles.value += 1
            self.cpu.addr_abs.value = self.cpu.pc.value + self.cpu.addr_rel.value

            cross_page_bound = (self.cpu.addr_abs.value & 0xff00) != (self.cpu.pc.value & 0xff00)
            if cross_page_bound:
                self.cpu.cycles.value += 1

            self.cpu.pc.value = self.cpu.addr_abs.value
        return c_uint8(0)

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x70: BVS(cpu, cycles=c_uint8(2), addr_mode=ams.am_rel)
        }


class CLC(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x18: CLC(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class CLD(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xd8: CLD(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class CLI(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x58: CLI(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class CLV(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xb8: CLV(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class CMP(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xc9: CMP(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0xc5: CMP(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0xd5: CMP(cpu, cycles=c_uint8(4), addr_mode=ams.am_zpx),
            0xcd: CMP(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
            0xdd: CMP(cpu, cycles=c_uint8(4), addr_mode=ams.am_abx),
            0xd9: CMP(cpu, cycles=c_uint8(4), addr_mode=ams.am_aby),
            0xc1: CMP(cpu, cycles=c_uint8(6), addr_mode=ams.am_izx),
            0xd1: CMP(cpu, cycles=c_uint8(5), addr_mode=ams.am_izy),
        }


class CPX(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xe0: CPX(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0xe4: CPX(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0xec: CPX(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
        }


class CPY(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xc0: CPY(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0xc4: CPY(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0xcc: CPY(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
        }


class DEC(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xc6: DEC(cpu, cycles=c_uint8(5), addr_mode=ams.am_zp0),
            0xd6: DEC(cpu, cycles=c_uint8(6), addr_mode=ams.am_zpx),
            0xce: DEC(cpu, cycles=c_uint8(6), addr_mode=ams.am_abs),
            0xde: DEC(cpu, cycles=c_uint8(7), addr_mode=ams.am_abx),
        }


class DEX(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xca: DEX(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class DEY(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x88: DEY(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class EOR(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x49: EOR(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0x45: EOR(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0x55: EOR(cpu, cycles=c_uint8(4), addr_mode=ams.am_zpx),
            0x4d: EOR(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
            0x5d: EOR(cpu, cycles=c_uint8(4), addr_mode=ams.am_abx),
            0x59: EOR(cpu, cycles=c_uint8(4), addr_mode=ams.am_aby),
            0x41: EOR(cpu, cycles=c_uint8(6), addr_mode=ams.am_izx),
            0x51: EOR(cpu, cycles=c_uint8(5), addr_mode=ams.am_izy),
        }


class INC(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xe6: INC(cpu, cycles=c_uint8(5), addr_mode=ams.am_zp0),
            0xf6: INC(cpu, cycles=c_uint8(6), addr_mode=ams.am_zpx),
            0xee: INC(cpu, cycles=c_uint8(6), addr_mode=ams.am_abs),
            0xfe: INC(cpu, cycles=c_uint8(7), addr_mode=ams.am_abx),
        }


class INX(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xe8: INX(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class INY(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xc8: INY(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class JMP(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x4c: JMP(cpu, cycles=c_uint8(3), addr_mode=ams.am_abs),
            0x6c: JMP(cpu, cycles=c_uint8(5), addr_mode=ams.am_ind),
        }


class JSR(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x20: JSR(cpu, cycles=c_uint8(6), addr_mode=ams.am_abs),
        }


class LDA(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xa9: LDA(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0xa5: LDA(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0xb5: LDA(cpu, cycles=c_uint8(4), addr_mode=ams.am_zpx),
            0xad: LDA(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
            0xbd: LDA(cpu, cycles=c_uint8(4), addr_mode=ams.am_abx),
            0xb9: LDA(cpu, cycles=c_uint8(4), addr_mode=ams.am_aby),
            0xa1: LDA(cpu, cycles=c_uint8(6), addr_mode=ams.am_izx),
            0xb1: LDA(cpu, cycles=c_uint8(5), addr_mode=ams.am_izy),
        }


class LDX(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xa2: LDX(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0xa6: LDX(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0xb6: LDX(cpu, cycles=c_uint8(4), addr_mode=ams.am_zpy),
            0xae: LDX(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
            0xbe: LDX(cpu, cycles=c_uint8(4), addr_mode=ams.am_aby),
        }


class LDY(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xa0: LDY(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0xa4: LDY(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0xb4: LDY(cpu, cycles=c_uint8(4), addr_mode=ams.am_zpx),
            0xac: LDY(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
            0xbc: LDY(cpu, cycles=c_uint8(4), addr_mode=ams.am_abx),
        }


class LSR(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x4a: LSR(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0x46: LSR(cpu, cycles=c_uint8(5), addr_mode=ams.am_zp0),
            0x56: LSR(cpu, cycles=c_uint8(6), addr_mode=ams.am_zpx),
            0x4e: LSR(cpu, cycles=c_uint8(6), addr_mode=ams.am_abs),
            0x5e: LSR(cpu, cycles=c_uint8(7), addr_mode=ams.am_abx),
        }


class NOP(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xea: NOP(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class ORA(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x09: ORA(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0x05: ORA(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0x15: ORA(cpu, cycles=c_uint8(4), addr_mode=ams.am_zpx),
            0x0d: ORA(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
            0x1d: ORA(cpu, cycles=c_uint8(4), addr_mode=ams.am_abx),
            0x19: ORA(cpu, cycles=c_uint8(4), addr_mode=ams.am_aby),
            0x01: ORA(cpu, cycles=c_uint8(6), addr_mode=ams.am_izx),
            0x11: ORA(cpu, cycles=c_uint8(5), addr_mode=ams.am_izy),
        }


class PHA(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x48: PHA(cpu, cycles=c_uint8(3), addr_mode=ams.am_imp)
        }


class PHP(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x08: PHP(cpu, cycles=c_uint8(3), addr_mode=ams.am_imp)
        }


class PLA(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x68: PLA(cpu, cycles=c_uint8(4), addr_mode=ams.am_imp)
        }


class PLP(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x28: PLP(cpu, cycles=c_uint8(4), addr_mode=ams.am_imp)
        }


class ROL(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x2a: ROL(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0x26: ROL(cpu, cycles=c_uint8(5), addr_mode=ams.am_zp0),
            0x36: ROL(cpu, cycles=c_uint8(6), addr_mode=ams.am_zpx),
            0x2e: ROL(cpu, cycles=c_uint8(6), addr_mode=ams.am_abs),
            0x3e: ROL(cpu, cycles=c_uint8(7), addr_mode=ams.am_abx),
        }


class ROR(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x6a: ROR(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0x66: ROR(cpu, cycles=c_uint8(5), addr_mode=ams.am_zp0),
            0x76: ROR(cpu, cycles=c_uint8(6), addr_mode=ams.am_zpx),
            0x6e: ROR(cpu, cycles=c_uint8(6), addr_mode=ams.am_abs),
            0x7e: ROR(cpu, cycles=c_uint8(7), addr_mode=ams.am_abx),
        }


class RTI(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x40: RTI(cpu, cycles=c_uint8(6), addr_mode=ams.am_imp)
        }


class RTS(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x60: RTS(cpu, cycles=c_uint8(6), addr_mode=ams.am_imp)
        }


class SBC(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xe9: SBC(cpu, cycles=c_uint8(2), addr_mode=ams.am_imm),
            0xe5: SBC(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0xf5: SBC(cpu, cycles=c_uint8(4), addr_mode=ams.am_zpx),
            0xed: SBC(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
            0xfd: SBC(cpu, cycles=c_uint8(4), addr_mode=ams.am_abx),
            0xf9: SBC(cpu, cycles=c_uint8(4), addr_mode=ams.am_aby),
            0xe1: SBC(cpu, cycles=c_uint8(6), addr_mode=ams.am_izx),
            0xf1: SBC(cpu, cycles=c_uint8(5), addr_mode=ams.am_izy),
        }


class SEC(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x38: SEC(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class SED(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xf8: SED(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class SEI(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x78: SEI(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class STA(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x85: STA(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0x95: STA(cpu, cycles=c_uint8(4), addr_mode=ams.am_zpx),
            0x8d: STA(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
            0x9d: STA(cpu, cycles=c_uint8(5), addr_mode=ams.am_abx),
            0x99: STA(cpu, cycles=c_uint8(5), addr_mode=ams.am_aby),
            0x81: STA(cpu, cycles=c_uint8(6), addr_mode=ams.am_izx),
            0x91: STA(cpu, cycles=c_uint8(6), addr_mode=ams.am_izy),
        }


class STX(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x86: STX(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0x96: STX(cpu, cycles=c_uint8(4), addr_mode=ams.am_zpy),
            0x8e: STX(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
        }


class STY(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x84: STY(cpu, cycles=c_uint8(3), addr_mode=ams.am_zp0),
            0x94: STY(cpu, cycles=c_uint8(4), addr_mode=ams.am_zpx),
            0x8c: STY(cpu, cycles=c_uint8(4), addr_mode=ams.am_abs),
        }


class TAX(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xaa: TAX(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class TAY(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xa8: TAY(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class TSX(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0xba: TSX(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class TXA(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x8a: TXA(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class TXS(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x9a: TXS(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class TYA(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {
            0x98: TYA(cpu, cycles=c_uint8(2), addr_mode=ams.am_imp)
        }


class XXX(Cpu6502Instruction):
    def operate(self):
        pass

    @staticmethod
    def opcodes_mapping(cpu: FakeDevice) -> Dict[int, Cpu6502Instruction]:
        return {}
