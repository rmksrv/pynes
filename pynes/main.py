import sys

from pynes.demo.demo_cpu6502_render import DemoCpu6502Render


def main():
    my_demo = DemoCpu6502Render()
    my_demo.setup(width=800, height=600)
    my_demo.run()


if __name__ == '__main__':
    sys.exit(main())
