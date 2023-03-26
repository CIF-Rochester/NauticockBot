# Extremely cursed number format. Used for sheets column name to number conversions: A = 1, AA = 27, AZ = 52, ...

def tob26(val: str) -> int:
    base26 = 0
    if not val:
        return base26
    scalar = len(val)-1
    for c in val:
        x = ord(c)-64
        base26 = base26 + pow(26,scalar)*x
        scalar-=1
    return base26


def str_from_b26(base26: int) -> str:
    out = ""
    while base26 > 0:
        rem = (base26-1)%26
        out = chr(int(rem+65)) + out
        base26 = int((base26-rem)/26)
    return out
