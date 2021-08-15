import pytest

from pynes.core.devices.bus import Bus
from pynes.core.devices.cpu6502 import Cpu6502
from pynes.core.devices.abstract_memory_device import AbstractMemoryDevice


@pytest.fixture()
def bus():
    cpu = Cpu6502()
    ram = AbstractMemoryDevice()
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
