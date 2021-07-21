from ctypes import c_ubyte, c_uint

from cpu6502 import CPU6502, CPU6502Opcodes
from memory import Memory


if __name__ == '__main__':
    # init devices
    cpu = CPU6502()
    mem = Memory()
    cpu.reset()
    print(cpu)

    # hardcoding test program (JSR)
    mem.write_byte(0xFFFC, c_ubyte(CPU6502Opcodes.JSR.value))
    mem.write_byte(0xFFFD, c_ubyte(0x42))
    mem.write_byte(0xFFFE, c_ubyte(0x42))
    mem.write_byte(0x4242, c_ubyte(CPU6502Opcodes.LDA_IM.value))
    mem.write_byte(0x4243, c_ubyte(0x84))

    # hardcoding test program (LDA_IM)
    # mem.write_byte(0xFFFC, c_ubyte(CPU6502Opcodes.LDA_IM.value))
    # mem.write_byte(0xFFFD, c_ubyte(0x42))

    # hardcoding test program (LDA_ZP)
    # mem.write(0xFFFC, c_ubyte(CPU6502Opcodes.LDA_ZP))
    # mem.write(0xFFFD, c_ubyte(0x42))
    # mem.write(0x0042, c_ubyte(0x84))

    # executing
    cpu.exec(mem, c_uint(9))
    print(cpu)
