"""Shared size facts for the Resize nodes (batch B). Pure Python. No node class in here."""
import math

_COMMON = ((1, 1), (5, 4), (4, 3), (3, 2), (16, 9), (2, 1), (21, 9))


def mult_text(width, height):
    """The biggest of 64, 32, 16, 8 that both sides are a multiple of, as words."""
    for m in (64, 32, 16, 8):
        if int(width) % m == 0 and int(height) % m == 0:
            return "multiple of %d" % m
    return "not a multiple of 8"


def ratio_text(width, height):
    """A short ratio such as 16:9 when it is simple, else a decimal such as 1.43:1."""
    width, height = int(width), int(height)
    g = math.gcd(width, height)
    a, b = width // g, height // g
    if max(a, b) <= 24:
        return "%d:%d" % (a, b)
    return "%.2f:1" % (width / height)


def size_facts(width, height):
    """Returns a plain phrase: megapixels, ratio and the multiple. Example: '1.05 MP, ratio 1:1, multiple of 64'."""
    width, height = int(width), int(height)
    return "%.2f MP, ratio %s, %s" % (width * height / 1e6, ratio_text(width, height), mult_text(width, height))
