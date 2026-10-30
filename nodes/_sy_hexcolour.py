"""Shared hex colour reader for the Image nodes. Pure Python, no torch."""


def parse_hex(text, field="colour"):
    """Reads '#rgb', '#rrggbb' (hash optional, any case). Returns (r, g, b) floats 0..1. Bad text raises ValueError naming `field`."""
    if not isinstance(text, str):
        raise ValueError("%s must be text like a web colour with 3 or 6 hex digits, got %r" % (field, text))
    s = text.strip()
    if s.startswith("#"):
        s = s[1:]
    if len(s) not in (3, 6) or any(ch not in "0123456789abcdefABCDEF" for ch in s):
        raise ValueError("%s must be 3 or 6 hex digits such as 'fa0' or 'ffaa00' (a leading # is fine), got %r" % (field, text))
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    return tuple(int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def to_hex(rgb):
    """(r, g, b) floats 0..1 -> text like a web colour."""
    vals = [min(255, max(0, int(round(v * 255.0)))) for v in rgb]
    return "#%02x%02x%02x" % tuple(vals)
