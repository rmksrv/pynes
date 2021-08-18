from pynes.core.devices import AbstractMemoryDevice


class Ram(AbstractMemoryDevice):
    min_address = 0x0000
    max_address = 0x1fff
