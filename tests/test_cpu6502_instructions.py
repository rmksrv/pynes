import pytest

from pynes.core.devices import Bus, Cpu6502, AbstractMemoryDevice


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
