from ctypes import c_uint8
from dataclasses import dataclass


@dataclass
class CartridgeHeader:
    name: str
    program_rom_chunks: c_uint8
    char_rom_chunks: c_uint8
    mapper_1: c_uint8
    mapper_2: c_uint8
    program_ram_size: c_uint8
    tv_system_1: c_uint8
    tv_system_2: c_uint8
    unused: str
