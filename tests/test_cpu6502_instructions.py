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
@pytest.mark.parametrize('init_data_value, init_a_value, init_c_value, '
                         'exp_a_value, exp_c_value, exp_z_value, exp_n_value, exp_v_value',
                         [
                             (0x00, 0x00, False, 0x00, False, True, False, False),
                         ])
def test_adc(cpu: Cpu6502, init_data_value: int, init_a_value: int, init_c_value: bool, exp_a_value: int,
             exp_c_value: bool, exp_z_value: bool, exp_n_value: bool, exp_v_value: bool):
    # cpu init state
    cpu.write(c_uint16(0x0000), c_uint8(init_data_value))
    cpu.a.value = init_a_value
    cpu.set_flag('c', init_c_value)

    op = cpu.lookup.get(0x69)
    res = op.operate()

    assert op.name == "ADC"
    assert res.value == 1
    assert cpu.a.value == exp_a_value
    assert cpu.get_flag('c') == exp_c_value
    assert cpu.get_flag('z') == exp_z_value
    assert cpu.get_flag('n') == exp_n_value
    assert cpu.get_flag('v') == exp_v_value


@pytest.mark.parametrize('init_data_value, init_a_value, exp_a_value, exp_z_value, exp_n_value',
                         [
                             (0x00, 0x00, 0x00, True, False),
                             (0xFF, 0xFF, 0xFF, False, True),
                             (0x0F, 0xF1, 0x01, False, False),
                         ])
def test_and(cpu: Cpu6502, init_data_value: int, init_a_value: int, exp_a_value: int,
             exp_z_value: bool, exp_n_value: bool):
    # cpu init state
    cpu.write(c_uint16(0x0000), c_uint8(init_data_value))
    cpu.a.value = init_a_value

    op = cpu.lookup.get(0x29)
    res = op.operate()

    assert op.name == "AND"
    assert res.value == 1
    assert cpu.a.value == exp_a_value
    assert cpu.get_flag('n') == exp_n_value
    assert cpu.get_flag('z') == exp_z_value


@pytest.mark.parametrize('init_c_value, init_addr_rel_value, init_pc_value, exp_pc_value, exp_cycles_value',
                         [
                             (True, 0x00FF, 0x0000, 0x0000, 0x00),
                             (False, 0x00FF, 0x0000, 0x00FF, 0x01),
                         ])
def test_bcc(cpu: Cpu6502, init_c_value: bool, init_addr_rel_value: int,
             init_pc_value: int, exp_pc_value: int, exp_cycles_value: int):
    # cpu init state
    cpu.set_flag('c', init_c_value)
    cpu.addr_rel.value = init_addr_rel_value
    cpu.pc.value = init_pc_value

    op = cpu.lookup.get(0x90)
    res = op.operate()

    assert op.name == "BCC"
    assert res.value == 0
    assert cpu.pc.value == exp_pc_value
    assert cpu.cycles.value == exp_cycles_value


@pytest.mark.parametrize('init_c_value, init_addr_rel_value, init_pc_value, exp_pc_value, exp_cycles_value',
                         [
                             (False, 0x00FF, 0x0000, 0x0000, 0x00),
                             (True, 0x00FF, 0x0000, 0x00FF, 0x01),
                         ])
def test_bcs(cpu: Cpu6502, init_c_value: bool, init_addr_rel_value: int,
             init_pc_value: int, exp_pc_value: int, exp_cycles_value: int):
    # cpu init state
    cpu.set_flag('c', init_c_value)
    cpu.addr_rel.value = init_addr_rel_value
    cpu.pc.value = init_pc_value

    op = cpu.lookup.get(0xb0)
    res = op.operate()

    assert op.name == "BCS"
    assert res.value == 0
    assert cpu.pc.value == exp_pc_value
    assert cpu.cycles.value == exp_cycles_value


@pytest.mark.parametrize('init_z_value, init_addr_rel_value, init_pc_value, exp_pc_value, exp_cycles_value',
                         [
                             (False, 0x00FF, 0x0000, 0x0000, 0x00),
                             (True, 0x00FF, 0x0000, 0x00FF, 0x01),
                         ])
def test_beq(cpu: Cpu6502, init_z_value: bool, init_addr_rel_value: int,
             init_pc_value: int, exp_pc_value: int, exp_cycles_value: int):
    # cpu init state
    cpu.set_flag('z', init_z_value)
    cpu.addr_rel.value = init_addr_rel_value
    cpu.pc.value = init_pc_value

    op = cpu.lookup.get(0xf0)
    res = op.operate()

    assert op.name == "BEQ"
    assert res.value == 0
    assert cpu.pc.value == exp_pc_value
    assert cpu.cycles.value == exp_cycles_value


@pytest.mark.parametrize('init_n_value, init_addr_rel_value, init_pc_value, exp_pc_value, exp_cycles_value',
                         [
                             (False, 0x00FF, 0x0000, 0x0000, 0x00),
                             (True, 0x00FF, 0x0000, 0x00FF, 0x01),
                         ])
def test_bmi(cpu: Cpu6502, init_n_value: bool, init_addr_rel_value: int,
             init_pc_value: int, exp_pc_value: int, exp_cycles_value: int):
    # cpu init state
    cpu.set_flag('n', init_n_value)
    cpu.addr_rel.value = init_addr_rel_value
    cpu.pc.value = init_pc_value

    op = cpu.lookup.get(0x30)
    res = op.operate()

    assert op.name == "BMI"
    assert res.value == 0
    assert cpu.pc.value == exp_pc_value
    assert cpu.cycles.value == exp_cycles_value


@pytest.mark.parametrize('init_z_value, init_addr_rel_value, init_pc_value, exp_pc_value, exp_cycles_value',
                         [
                             (True, 0x00FF, 0x0000, 0x0000, 0x00),
                             (False, 0x00FF, 0x0000, 0x00FF, 0x01),
                         ])
def test_bne(cpu: Cpu6502, init_z_value: bool, init_addr_rel_value: int,
             init_pc_value: int, exp_pc_value: int, exp_cycles_value: int):
    # cpu init state
    cpu.set_flag('z', init_z_value)
    cpu.addr_rel.value = init_addr_rel_value
    cpu.pc.value = init_pc_value

    op = cpu.lookup.get(0xd0)
    res = op.operate()

    assert op.name == "BNE"
    assert res.value == 0
    assert cpu.pc.value == exp_pc_value
    assert cpu.cycles.value == exp_cycles_value


@pytest.mark.parametrize('init_n_value, init_addr_rel_value, init_pc_value, exp_pc_value, exp_cycles_value',
                         [
                             (True, 0x00FF, 0x0000, 0x0000, 0x00),
                             (False, 0x00FF, 0x0000, 0x00FF, 0x01),
                         ])
def test_bpl(cpu: Cpu6502, init_n_value: bool, init_addr_rel_value: int,
             init_pc_value: int, exp_pc_value: int, exp_cycles_value: int):
    # cpu init state
    cpu.set_flag('n', init_n_value)
    cpu.addr_rel.value = init_addr_rel_value
    cpu.pc.value = init_pc_value

    op = cpu.lookup.get(0x10)
    res = op.operate()

    assert op.name == "BPL"
    assert res.value == 0
    assert cpu.pc.value == exp_pc_value
    assert cpu.cycles.value == exp_cycles_value


@pytest.mark.parametrize('init_v_value, init_addr_rel_value, init_pc_value, exp_pc_value, exp_cycles_value',
                         [
                             (True, 0x00FF, 0x0000, 0x0000, 0x00),
                             (False, 0x00FF, 0x0000, 0x00FF, 0x01),
                         ])
def test_bvc(cpu: Cpu6502, init_v_value: bool, init_addr_rel_value: int,
             init_pc_value: int, exp_pc_value: int, exp_cycles_value: int):
    # cpu init state
    cpu.set_flag('v', init_v_value)
    cpu.addr_rel.value = init_addr_rel_value
    cpu.pc.value = init_pc_value

    op = cpu.lookup.get(0x50)
    res = op.operate()

    assert op.name == "BVC"
    assert res.value == 0
    assert cpu.pc.value == exp_pc_value
    assert cpu.cycles.value == exp_cycles_value


@pytest.mark.parametrize('init_v_value, init_addr_rel_value, init_pc_value, exp_pc_value, exp_cycles_value',
                         [
                             (False, 0x00FF, 0x0000, 0x0000, 0x00),
                             (True, 0x00FF, 0x0000, 0x00FF, 0x01),
                         ])
def test_bvs(cpu: Cpu6502, init_v_value: bool, init_addr_rel_value: int,
             init_pc_value: int, exp_pc_value: int, exp_cycles_value: int):
    # cpu init state
    cpu.set_flag('v', init_v_value)
    cpu.addr_rel.value = init_addr_rel_value
    cpu.pc.value = init_pc_value

    op = cpu.lookup.get(0x70)
    res = op.operate()

    assert op.name == "BVS"
    assert res.value == 0
    assert cpu.pc.value == exp_pc_value
    assert cpu.cycles.value == exp_cycles_value


@pytest.mark.parametrize('init_c_value', [True, False])
def test_clc(cpu: Cpu6502, init_c_value: bool):
    # cpu init state
    cpu.set_flag('c', init_c_value)

    op = cpu.lookup.get(0x18)
    res = op.operate()

    assert op.name == "CLC"
    assert res.value == 0
    assert not cpu.get_flag('c')


@pytest.mark.parametrize('init_d_value', [True, False])
def test_cld(cpu: Cpu6502, init_d_value: bool):
    # cpu init state
    cpu.set_flag('d', init_d_value)

    op = cpu.lookup.get(0xd8)
    res = op.operate()

    assert op.name == "CLD"
    assert res.value == 0
    assert not cpu.get_flag('d')


@pytest.mark.parametrize('init_i_value', [True, False])
def test_cli(cpu: Cpu6502, init_i_value: bool):
    # cpu init state
    cpu.set_flag('i', init_i_value)

    op = cpu.lookup.get(0x58)
    res = op.operate()

    assert op.name == "CLI"
    assert res.value == 0
    assert not cpu.get_flag('i')


@pytest.mark.parametrize('init_v_value', [True, False])
def test_clv(cpu: Cpu6502, init_v_value: bool):
    # cpu init state
    cpu.set_flag('v', init_v_value)

    op = cpu.lookup.get(0xb8)
    res = op.operate()

    assert op.name == "CLV"
    assert res.value == 0
    assert not cpu.get_flag('v')


@pytest.mark.parametrize('init_sp_value, init_a_value',
                         [
                             (0x10, 0xFF),
                             (0x00, 0xF0),
                             (0xFF, 0x0F),
                         ])
def test_pha(cpu: Cpu6502, init_sp_value: int, init_a_value: int):
    # cpu init state
    cpu.sp.value = init_sp_value
    cpu.a.value = init_a_value

    op = cpu.lookup.get(0x48)
    res = op.operate()

    assert op.name == "PHA"
    assert res.value == 0
    assert cpu.sp.value == c_uint8(init_sp_value - 1).value
    assert cpu.read(c_uint16(0x0100 + init_sp_value)).value == init_a_value


@pytest.mark.parametrize('init_sp_value, init_data',
                         [
                             (0x10, 0xFF),
                             (0x00, 0xF0),
                             (0xFF, 0x0F),
                         ])
def test_pla(cpu: Cpu6502, init_sp_value: int, init_data: int):
    # cpu init state
    cpu.sp.value = init_sp_value
    cpu.write(c_uint16(0x0100 + init_sp_value), c_uint8(init_data))

    op = cpu.lookup.get(0x68)
    res = op.operate()

    assert op.name == "PLA"
    assert res.value == 0
    assert cpu.sp.value == c_uint8(init_sp_value + 1).value
    assert cpu.a.value == c_uint8(init_data).value


@pytest.mark.skip
def test_sbc(cpu: Cpu6502):
    # TODO create tests for ADC/SBC
    pass


@pytest.mark.parametrize('init_c_value', [True, False])
def test_sec(cpu: Cpu6502, init_c_value: bool):
    # cpu init state
    cpu.set_flag('c', init_c_value)

    op = cpu.lookup.get(0x38)
    res = op.operate()

    assert op.name == "SEC"
    assert res.value == 0
    assert cpu.get_flag('c')


@pytest.mark.parametrize('init_d_value', [True, False])
def test_sed(cpu: Cpu6502, init_d_value: bool):
    # cpu init state
    cpu.set_flag('d', init_d_value)

    op = cpu.lookup.get(0xf8)
    res = op.operate()

    assert op.name == "SED"
    assert res.value == 0
    assert cpu.get_flag('d')


@pytest.mark.parametrize('init_i_value', [True, False])
def test_sei(cpu: Cpu6502, init_i_value: bool):
    # cpu init state
    cpu.set_flag('d', init_i_value)

    op = cpu.lookup.get(0x78)
    res = op.operate()

    assert op.name == "SEI"
    assert res.value == 0
    assert cpu.get_flag('i')
