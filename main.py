from ctypes import c_uint8, c_uint16


from bus import Bus
from cpu6502 import Cpu6502
from ram import Ram

if __name__ == '__main__':
    test_cpu = Cpu6502()
    test_ram = Ram()
    test_bus = Bus()

    print(test_bus)
    test_cpu.connect_to_bus(test_bus)
    test_ram.connect_to_bus(test_bus)
    print(test_bus)

    foo = test_cpu.read_from_ram(c_uint16(0x0000))
    print(foo)
