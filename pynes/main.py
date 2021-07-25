from pynes.core.bus import Bus
from pynes.core.cpu6502 import Cpu6502
from pynes.core.ram import Ram

if __name__ == '__main__':
    test_cpu = Cpu6502()
    test_ram = Ram()
    test_bus = Bus()

    test_cpu.connect_to_bus(test_bus)
    test_ram.connect_to_bus(test_bus)

    print(f"z: {test_cpu.z.value}")

    test_instr = test_cpu.lookup.get(0x29)
    test_instr.operate()
    print("AND was operated...")

    print(f"z: {test_cpu.z.value}")
