FLAGS = ('c', 'z', 'i', 'd', 'b', 'u', 'v', 'n')


def get_mask(flag: str) -> int:
    """
    Gets bit mask for flags of Cpu6502
    """
    shift_amt = FLAGS.index(flag) if flag in FLAGS else len(FLAGS)
    return 1 << shift_amt
