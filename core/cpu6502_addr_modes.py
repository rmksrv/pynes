from ctypes import c_uint8, c_uint16

from core.device.fake_device import FakeDevice

ADDR_MODE_EXIT_SUCCESS:        c_uint8 = c_uint8(0)
ADDR_MODE_EXIT_ADD_CYCLE_NEED: c_uint8 = c_uint8(0)


def am_imp(cpu: FakeDevice) -> c_uint8:
    """
    Implicit/Accumulator Addressing
    :param cpu:
    :return:
    """
    cpu.fetched = cpu.a
    return ADDR_MODE_EXIT_SUCCESS


def am_imm(cpu: FakeDevice) -> c_uint8:
    """
    Immediate Addressing
    :param cpu:
    :return:
    """
    cpu.addr_abs = cpu.pc
    cpu.pc += 1
    return ADDR_MODE_EXIT_SUCCESS


def am_zp0(cpu: FakeDevice) -> c_uint8:
    """
    Zero Page Addressing
    :param cpu:
    :return:
    """
    cpu.addr_abs = cpu.read(cpu.pc)
    cpu.pc += 1
    cpu.addr_abs.value &= 0x00FF  # get 00 page with FF offset
    return ADDR_MODE_EXIT_SUCCESS


def am_zpx(cpu: FakeDevice) -> c_uint8:
    """
    Zero Page with X offset Addressing
    :param cpu:
    :return:
    """
    cpu.addr_abs = c_uint16(cpu.read(cpu.pc).value + cpu.x.value)
    cpu.pc += 1
    cpu.addr_abs.value &= 0x00FF  # get 00 page with FF offset
    return ADDR_MODE_EXIT_SUCCESS


def am_zpy(cpu: FakeDevice) -> c_uint8:
    """
    Zero Page with Y offset Addressing
    :param cpu:
    :return:
    """
    cpu.addr_abs = c_uint16(cpu.read(cpu.pc).value + cpu.y.value)
    cpu.pc += 1
    cpu.addr_abs.value &= 0x00FF  # get 00 page with FF offset
    return ADDR_MODE_EXIT_SUCCESS


def am_abs(cpu: FakeDevice) -> c_uint8:
    """
    Absolute Addressing
    :param cpu:
    :return:
    """
    lo = cpu.read(cpu.pc)
    cpu.pc += 1
    hi = cpu.read(cpu.pc)
    cpu.pc += 1

    cpu.addr_abs = c_uint16((hi.value << 8) | lo.value)

    return ADDR_MODE_EXIT_SUCCESS


def am_abx(cpu: FakeDevice) -> c_uint8:
    """
    Absolute with X offset Addressing
    :param cpu:
    :return:
    """
    lo = cpu.read(cpu.pc)
    cpu.pc += 1
    hi = cpu.read(cpu.pc)
    cpu.pc += 1

    cpu.addr_abs = c_uint16(((hi.value << 8) | lo.value) + cpu.x.value)

    return ADDR_MODE_EXIT_SUCCESS if (cpu.addr_abs.value & 0xFF00) == (hi.value << 8) else ADDR_MODE_EXIT_ADD_CYCLE_NEED


def am_aby(cpu: FakeDevice) -> c_uint8:
    """
    Absolute with Y offset Addressing
    :param cpu:
    :return:
    """
    lo = cpu.read(cpu.pc)
    cpu.pc += 1
    hi = cpu.read(cpu.pc)
    cpu.pc += 1

    cpu.addr_abs = c_uint16(((hi.value << 8) | lo.value) + cpu.y.value)

    return ADDR_MODE_EXIT_SUCCESS if (cpu.addr_abs.value & 0xFF00) == (hi.value << 8) else ADDR_MODE_EXIT_ADD_CYCLE_NEED


def am_ind(cpu: FakeDevice) -> c_uint8:
    """
    Indirect Addressing
    :param cpu:
    :return:
    """
    ptr_lo = cpu.read(cpu.pc)
    cpu.pc += 1
    ptr_hi = cpu.read(cpu.pc)
    cpu.pc += 1

    ptr = c_uint16((ptr_hi.value << 8) | ptr_lo.value)

    # Page boundary hardware bug else normal behaviour
    cpu.addr_abs = c_uint16((cpu.read(c_uint16(ptr.value & 0xFF00)).value << 8) |
                            cpu.read(ptr).value) if ptr_lo.value == 0x00FF \
        else c_uint16((cpu.read(c_uint16(ptr.value + 1)).value << 8) |
                      cpu.read(ptr).value)

    return ADDR_MODE_EXIT_SUCCESS


def am_izx(cpu: FakeDevice) -> c_uint8:
    """
    Indirect X Addressing
    :param cpu:
    :return:
    """
    t = cpu.read(cpu.pc)
    cpu.pc += 1

    lo = cpu.read(c_uint16(
        (t.value + c_uint16(cpu.x.value).value) & 0x00FF)
    )
    hi = cpu.read(c_uint16(
        (t.value + c_uint16(cpu.x.value).value + 1) & 0x00FF)
    )

    cpu.addr_abs = c_uint16((hi.value << 8) | lo.value)

    return ADDR_MODE_EXIT_SUCCESS


def am_izy(cpu: FakeDevice) -> c_uint8:
    """
    Indirect Y Addressing
    :param cpu:
    :return:
    """
    t = cpu.read(cpu.pc)
    cpu.pc += 1

    lo = cpu.read(c_uint16(t.value & 0x00FF))
    hi = cpu.read(c_uint16((t.value + 1) & 0x00FF))

    cpu.addr_abs = c_uint16(((hi.value << 8) | lo.value) + cpu.y.value)

    return ADDR_MODE_EXIT_SUCCESS if (cpu.addr_abs.value & 0xFF00) == (hi.value << 8) else ADDR_MODE_EXIT_ADD_CYCLE_NEED


def am_rel(cpu: FakeDevice) -> c_uint8:
    """
    Relative Addressing
    :param cpu:
    :return:
    """
    cpu.addr_rel = cpu.read(cpu.pc)
    cpu.pc += 1
    if cpu.addr_rel.value & 0x80:
        cpu.addr_rel.value |= 0xFF00
    return ADDR_MODE_EXIT_SUCCESS
