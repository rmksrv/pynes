import pytest

from pynes.core.devices import Bus, Cpu6502, Ram, Ppu2C02, Cartridge


@pytest.fixture()
def bus():
    bus = Bus()
    Cpu6502().connect_to_bus(bus)
    Ppu2C02().connect_to_bus(bus)
    Ram().connect_to_bus(bus)
    Cartridge().connect_to_bus(bus)
    yield bus


@pytest.fixture()
def cpu(bus: Bus):
    yield bus.get_cpu6502()


# TESTS
def test_instructions(cpu: Cpu6502):
    pass
