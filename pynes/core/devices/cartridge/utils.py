from typing import BinaryIO, List


def instructions_list_from_nes_io(nesfile_io: BinaryIO) -> List[int]:
    instructions = []
    byte = nesfile_io.read(1)
    while byte:
        instructions.append(int(byte.hex(), 16))
        byte = nesfile_io.read(1)
    return instructions
