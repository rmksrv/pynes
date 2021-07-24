import pytest
from ctypes import c_uint8, c_uint16

from core.cpu6502 import Cpu6502
from core.ram import Ram
from core.bus import Bus


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


@pytest.mark.parametrize('data_value, old_a_value, new_a_value, new_z_value, new_n_value',
                         [
                             (0x00, 0x00, 0x00, True, False),
                             (0xFF, 0xFF, 0xFF, False, True),
                             (0x0F, 0xF1, 0x01, False, False),
                         ])
def test_and(cpu: Cpu6502, data_value: int, old_a_value: int, new_a_value: int,
             new_z_value: bool, new_n_value: bool):
    expected_res_val = 1
    # cpu init state
    cpu.write(c_uint16(0x0000), c_uint8(data_value))
    cpu.a.value = old_a_value

    res = cpu.lookup.get(0x29).operate()

    assert res.value == expected_res_val
    assert cpu.a.value == new_a_value
    assert cpu.n.value == new_n_value
    assert cpu.z.value == new_z_value
