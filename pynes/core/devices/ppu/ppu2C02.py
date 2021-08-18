from pynes.core.devices import Bus, AbstractDevice
from pynes.core.devices.ppu.nametable import PpuNametable
from pynes.core.devices.ppu.palettes import PpuPalettes
from pynes.core.devices.ppu.pattern import PpuPattern


class Ppu2C02(AbstractDevice):

    def __init__(self):
        super().__init__()
        self.internal_bus = Bus()
        self.connect_to_bus(self.internal_bus)
        PpuPattern().connect_to_bus(self.internal_bus)
        PpuNametable().connect_to_bus(self.internal_bus)
        PpuPalettes().connect_to_bus(self.internal_bus)
