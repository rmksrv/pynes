import pytest
from ctypes import c_uint8, c_uint16

from pynes.core.cpu6502 import Cpu6502
from pynes.core.ram import Ram
from pynes.core.bus import Bus


@pytest.fixture()
def bus():
    cpu = Cpu6502()
    ram = Ram()
    bus = Bus()
    cpu.connect_to_bus(bus)
    ram.connect_to_bus(bus)
    yield bus


@pytest.fixture()
def cpu(bus: Bus):
    yield bus.get_cpu6502()


# TESTS
def test_instructions(cpu: Cpu6502):
    pass
