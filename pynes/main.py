import sys

from pynes.demos.demo_cpu6502_render import DemoCpu6502Render
# from pynes.core.devices import Bus, Cpu6502, Ppu2C02, Ram, Cartridge
# from pynes.demos.demo_cpu6502_render import sample_6502_program



def main():
    my_demo = DemoCpu6502Render()
    my_demo.setup(width=800, height=600)
    my_demo.load_rom(start=0x4020)
    my_demo.run()
    # nes = Bus()
    #
    # Cpu6502().connect_to_bus(nes)
    # Ppu2C02().connect_to_bus(nes)
    # Ram().connect_to_bus(nes)
    # Cartridge().connect_to_bus(nes)
    #
    # nes.get_cpu6502().load_rom(sample_6502_program())
    #
    # print(nes)


if __name__ == '__main__':
    sys.exit(main())
