from pynes.core.devices import Bus, AbstractMemoryDevice


class Ppu2C02(AbstractMemoryDevice):
    min_address = 0x2000
    max_address = 0x2007

    def __init__(self):
        super().__init__()
        self.ppu_bus = Bus()
        self.connect_to_bus(self.ppu_bus)
