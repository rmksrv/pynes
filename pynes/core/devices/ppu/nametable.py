from pynes.core.devices import AbstractMemoryDevice


class PpuNametable(AbstractMemoryDevice):
    min_address = 0x2000
    max_address = 0x2fff
