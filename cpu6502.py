from ctypes import c_ubyte, c_ushort, c_bool, c_uint
from enum import Enum

from memory import Memory


class CPU6502:
    PC_INIT: int = 0xFFFC
    SP_INIT: int = 0x00
    # masks
    SIGN_MASK: int = 0b10000000

    def __init__(self):
        self.pc: c_ushort = c_ushort(CPU6502.PC_INIT)  # program counter
        self.sp: c_ubyte = c_ubyte(CPU6502.SP_INIT)  # stack pointer
        self.a: c_ubyte = c_ubyte(0)  # accumulator
        self.x: c_ubyte = c_ubyte(0)  # registers
        self.y: c_ubyte = c_ubyte(0)
        # status
        self.c: c_bool = c_bool(False)  # carry bit
        self.z: c_bool = c_bool(False)  # zero
        self.i: c_bool = c_bool(False)  # disable interrupts
        self.d: c_bool = c_bool(False)  # decimal mode
        self.b: c_bool = c_bool(False)  # break
        self.u: c_bool = c_bool(False)  # unused
        self.v: c_bool = c_bool(False)  # overflow
        self.n: c_bool = c_bool(False)  # negative

    def reset(self) -> None:
        self.pc = c_ushort(CPU6502.PC_INIT)
        self.sp = c_ushort(CPU6502.SP_INIT)
        self.a = self.x = self.y = c_ubyte(0)
        self.c = self.z = self.i = self.d = self.b = self.v = self.n = c_bool(False)

    def exec(self, m: Memory, cycles: c_uint) -> None:
        while cycles.value > 0:
            ins: c_ubyte = self.fetch_byte(m, cycles)
            print(f"cycles: {cycles.value}; pc: {self.pc.value}; ins: {hex(ins.value)}")
            if ins.value == CPU6502Opcodes.LDA_IM.value:
                value = self.fetch_byte(m, cycles)
                self.a = value
                self._lda_set_status()
            elif ins.value == CPU6502Opcodes.LDA_ZP.value:
                zero_page_address = self.fetch_byte(m, cycles)
                self.a = self.read_byte(m, cycles, zero_page_address)
                self._lda_set_status()
            elif ins.value == CPU6502Opcodes.LDA_ZPX.value:
                zero_page_address = c_ubyte(self.fetch_byte(m, cycles).value + self.x.value)
                cycles.value -= 1
                self.a = self.read_byte(m, cycles, zero_page_address)
                self._lda_set_status()
            elif ins.value == CPU6502Opcodes.JSR.value:
                subaddr = self.fetch_word(m, cycles)
                m.write_word(self.pc.value - 1, c_ushort(self.sp.value + 1), cycles)
                self.pc= subaddr
                cycles.value -= 1
            # else:
                # print(f"Instruction \"{hex(ins.value)}\" was not handled")

    def read_byte(self, m: Memory, cycles: c_uint, addr: c_ubyte) -> c_ubyte:
        data = m.read_byte(addr.value)
        cycles.value -= 1
        return data

    def fetch_byte(self, m: Memory, cycles: c_uint) -> c_ubyte:
        data = m.read_byte(self.pc.value)
        cycles.value -= 1
        self.pc.value += 1
        return data

    def fetch_word(self, m: Memory, cycles: c_uint) -> c_ushort:
        data = m.read_byte(self.pc.value)
        self.pc.value += 1
        data = data.value | m.read_byte(self.pc.value).value << 8
        self.pc.value += 1
        cycles.value += 2
        return c_ushort(data)

    def _lda_set_status(self) -> None:
        self.z.value = bool(self.a.value == 0)
        self.n.value = bool((self.a.value & CPU6502.SIGN_MASK) > 0)

    def __repr__(self) -> str:
        return f"CPU6502(pc:{self.pc.value}; sp:{self.sp.value}; a:{self.a.value}; x:{self.x.value}; " \
               f"y:{self.y.value}; status:{int(self.c.value)}{int(self.z.value)}{int(self.i.value)}" \
               f"{int(self.d.value)}{int(self.b.value)}{int(self.u.value)}{int(self.v.value)}{int(self.n.value)})"


class CPU6502Opcodes(Enum):
    LDA_IM  = 0xA9
    LDA_ZP  = 0xA5
    LDA_ZPX = 0xB5
    JSR     = 0x20
