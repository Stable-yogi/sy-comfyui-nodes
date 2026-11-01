"""Size Text SY: turns a byte count into easy text such as 1.5 GB."""
UNITS = ("B", "KB", "MB", "GB", "TB", "PB")
FORCE_UNITS = ("auto", "B", "KB", "MB", "GB", "TB")
BASES = ("1024", "1000")

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def size_text(n, base, decimals, unit="auto"):
    """Pure function. 0 -> '0 B', 1024 (base 1024) -> '1.0 KB'. Below one unit the plain byte count shows."""
    if str(base) not in BASES:
        raise ValueError("base must be 1024 or 1000, got %r" % (base,))
    if not 0 <= decimals <= 4:
        raise ValueError("decimals must be between 0 and 4, got %s" % decimals)
    if n < 0:
        raise ValueError("bytes cannot be negative, got %s" % n)
    b = int(base)
    if unit != "auto":
        if unit not in FORCE_UNITS:
            raise ValueError("unit must be one of: %s, got %r" % (", ".join(FORCE_UNITS), unit))
        return "%.*f %s" % (decimals, n / float(b ** UNITS.index(unit)), unit)
    if n < b:
        return "%d B" % n
    value = float(n)
    unit = 0
    while value >= b and unit < len(UNITS) - 1:
        value /= b
        unit += 1
    # rounding must not produce "1024.0 KB": move up one unit instead
    if round(value, decimals) >= b and unit < len(UNITS) - 1:
        value /= b
        unit += 1
    return "%.*f %s" % (decimals, value, UNITS[unit])


def size_report(n, base, decimals, unit="auto"):
    """Pure function. Returns (text, number, info). number is the size in the unit shown, as a decimal."""
    text = size_text(n, base, decimals, unit)
    number = float(text.split(" ")[0])
    return text, number, "%d bytes = %s (%s base)" % (n, text, base)


class SYSizeText:
    DESCRIPTION = "Turns a number of bytes into easy text such as 1.5 GB. Useful for file size labels. Pick a fixed unit (like GB) to compare sizes, and use the number output for maths. The info line shows the bytes and the base used."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "FLOAT", "STRING")
    RETURN_NAMES = ("text", "number", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "bytes": ("INT", {"default": 1048576, "min": 0, "max": 9007199254740991, "tooltip": "The size in bytes."}),
                "base": (list(BASES), {"default": "1024", "tooltip": "1024 is what most computers use; 1000 is what disk makers use."}),
                "decimals": ("INT", {"default": 1, "min": 0, "max": 4, "tooltip": "How many digits to show after the decimal point."}),
            },
            "optional": {
                "unit": (list(FORCE_UNITS), {"default": "auto", "tooltip": "auto picks the best unit. Choose GB to always get gigabytes, like 0.5 GB."}),
            },
        }

    def run(self, bytes, base, decimals, unit="auto"):
        return size_report(bytes, base, decimals, unit)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SizeText", SYSizeText)
NODE_DISPLAY_NAME_MAPPINGS["SYSizeText"] = "Size Text SY"
