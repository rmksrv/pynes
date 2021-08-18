import sys

from pynes.demos.demo_cpu6502_render import DemoCpu6502Render


def main():
    my_demo = DemoCpu6502Render()
    my_demo.setup(width=800, height=600)
    # my_demo.load_rom(start=0x4020)
    my_demo.load_rom()
    my_demo.run()


if __name__ == '__main__':
    sys.exit(main())
