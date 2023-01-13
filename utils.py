from types import NoneType


def to_int(value): return int(float(value))


def is_number(s):
    if not s or type(s) == NoneType:
        return False
    try:
        float(s)
    except ValueError:
        return False
    return True
