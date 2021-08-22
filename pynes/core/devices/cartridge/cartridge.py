import os
from ctypes import c_uint8, c_uint16
from typing import List, Union

from pynes.core.devices import AbstractMemoryDevice
from pynes.core.devices.cartridge.utils import instructions_list_from_nes_io


class Cartridge(AbstractMemoryDevice):
    min_address = 0x4020
    max_address = 0xffff

    def __init__(self):
        super().__init__()
        self.mapper_id = 0
        self.program_banks = 0
        self.char_banks = 0

    @property
    def program_memory(self) -> List[c_uint8]:
        # FIXME
        return self.data[self.min_address:self.max_address]

    @property
    def char_memory(self) -> List[c_uint8]:
        # FIXME
        return self.data[self.min_address:self.max_address]

    def load_rom(self, filename: Union[str, bytes, os.PathLike], start: int = min_address) -> None:
        raw_opcodes = []
        with open(filename, 'rb') as file_is:
            raw_opcodes = instructions_list_from_nes_io(file_is)

        for addr, opc in enumerate(raw_opcodes):
            self.write(c_uint16(start + addr), c_uint8(opc))
