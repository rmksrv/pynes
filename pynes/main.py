from ctypes import c_uint16, c_uint8

from pynes.core.bus import Bus
from pynes.core.cpu6502 import Cpu6502
from pynes.core.ram import Ram
from pynes.demo.demo_cpu6502_render import DemoCpu6502Render


def write_sample_6502_prog_to_cpu(cpu: Cpu6502) -> None:
    prog = [0xA2, 0x0A, 0x8E, 0x00, 0x00, 0xA2, 0x03, 0x8E,
            0x01, 0x00, 0xAC, 0x00, 0x00, 0xA9, 0x00, 0x18,
            0x6D, 0x01, 0x00, 0x88, 0xD0, 0xFA, 0x8D, 0x02,
            0x00, 0xEA, 0xEA, 0xEA]
    for addr, opc in enumerate(prog):
        cpu.write(c_uint16(addr), c_uint8(opc))


if __name__ == '__main__':
    test_cpu = Cpu6502()
    test_ram = Ram()
    test_bus = Bus()

    test_cpu.connect_to_bus(test_bus)
    test_ram.connect_to_bus(test_bus)

    # print("Created test Bus:")
    # print(test_bus)
    # print("Writing test prog")
    write_sample_6502_prog_to_cpu(test_cpu)
    for _, string in test_cpu.disassemble(0x00, 0x1f).items():
        print(string)

    my_demo = DemoCpu6502Render()
    my_demo.setup()
    write_sample_6502_prog_to_cpu(my_demo.bus.get_cpu6502())
    my_demo.run()
