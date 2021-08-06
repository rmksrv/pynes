def get_mask(flag: str) -> int:
    """
    Gets bit mask for flags of Cpu6502
    """
    flags = ['c', 'z', 'i', 'd', 'b', 'u', 'v', 'n']
    shift_amt = flags.index(flag)
    return 1 << shift_amt
