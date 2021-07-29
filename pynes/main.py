from pynes.core.bus import Bus
from pynes.core.cpu6502 import Cpu6502
from pynes.core.ram import Ram

if __name__ == '__main__':
    test_cpu = Cpu6502()
    test_ram = Ram()
    test_bus = Bus()

    test_cpu.connect_to_bus(test_bus)
    test_ram.connect_to_bus(test_bus)

    print("Created test Bus:")
    print(test_bus)

    # test_cpu.c.value = True
    test_cpu.set_flag('c', True)
    op = test_cpu.lookup.get(0xb0)
    print(op)
    res = op.operate()
