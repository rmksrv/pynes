from typing import BinaryIO, List

FLAGS = ('c', 'z', 'i', 'd', 'b', 'u', 'v', 'n')


def get_mask(flag: str) -> int:
    """
    Gets bit mask for flags of Cpu6502
    """
    shift_amt = FLAGS.index(flag) if flag in FLAGS else len(FLAGS)
    return 1 << shift_amt


def instructions_list_from_nes_io(nesfile_io: BinaryIO) -> List[int]:
    instrs = []
    byte = nesfile_io.read(1)
    while byte:
        instrs.append(int(byte.hex(), 16))
        byte = nesfile_io.read(1)
    return instrs
