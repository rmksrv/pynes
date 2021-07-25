from typing import Optional

from pynes.core.device.fake_device import FakeDevice


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
