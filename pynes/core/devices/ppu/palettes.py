from pynes.core.devices import AbstractMemoryDevice


class PpuPalettes(AbstractMemoryDevice):
    min_address = 0x3f00
    max_address = 0x3fff
