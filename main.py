from ctypes import c_uint8

from core.bus import Bus
from core.cpu6502 import Cpu6502
from core.ram import Ram
from core import cpu6502_addr_modes as addr_modes
from core.cpu6502_instructions import AND

if __name__ == '__main__':
    test_cpu = Cpu6502()
    test_ram = Ram()
    test_bus = Bus()

    test_cpu.connect_to_bus(test_bus)
    test_ram.connect_to_bus(test_bus)
    print(test_bus)
    print(test_cpu)

    test_instr = AND(cpu=test_cpu,
                     cycles=c_uint8(5),
                     addr_mode=addr_modes.am_aby)
    test_instr.operate()
    print("AND was operated...")

    print(test_bus)
    print(test_cpu)

    print()
    # foo = test_cpu.read(c_uint16(0x0000))
    # print(foo)
