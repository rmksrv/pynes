from abc import ABC
from typing import Optional


class FakeDevice(ABC):
    """
    tl;dr: FakeDevice == Device
    Duplicating class for device.Device. Need this one to avoid circular imports:
        main.py -> import Bus -> import Device -> import Bus -> ...
    We could really just don't use it, but with this we keep type declarations inside Bus class
    """
    NAME_DEVICE_RAM     = 'Ram'
    NAME_DEVICE_CPU6502 = 'Cpu6502'


class Bus:

    def __init__(self):
        self.devices = {}

    def register_device(self, d: FakeDevice) -> None:
        self.devices.update({type(d).__name__: d})

    def get_ram(self) -> Optional[FakeDevice]:
        return self.devices.get(FakeDevice.NAME_DEVICE_RAM)

    def get_cpu6502(self) -> Optional[FakeDevice]:
        return self.devices.get(FakeDevice.NAME_DEVICE_CPU6502)

    def __repr__(self) -> str:
        return "Bus({i}) {d}".format(i=id(self),
                                     d=self.devices)
