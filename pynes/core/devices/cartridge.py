from pynes.core.devices import AbstractMemoryDevice


class Cartridge(AbstractMemoryDevice):
    min_address = 0x4020
    max_address = 0xffff
