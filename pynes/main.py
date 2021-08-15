import sys

from pynes.demo.demo_cpu6502_render import DemoCpu6502Render


def main():
    my_demo = DemoCpu6502Render()
    my_demo.setup(width=800, height=600)
    my_demo.load_rom(rom=[0xa9, 0x01, 0x8d, 0x00,
                          0x02, 0xa9, 0x05, 0x8d,
                          0x01, 0x02, 0xa9, 0x08,
                          0x8d, 0x02, 0x02])
    my_demo.run()


if __name__ == '__main__':
    sys.exit(main())
