"""Humanize Number SY: shows raw numbers as file sizes, durations or counts people can read."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

KINDS = ["bytes", "seconds", "count"]
_BYTE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]
_COUNT_UNITS = ["", "k", "M", "B"]


def _scale(v, base, units, decimals):
    i = 0
    while v >= base and i < len(units) - 1:
        v /= base
        i += 1
    if i < len(units) - 1 and round(v, decimals) >= base:  # 1023.99 KB must not print as 1024.0 KB
        v /= base
        i += 1
    return v, i


def _duration(v, decimals):
    if round(v, decimals) < 60:
        return "%.*f s" % (decimals, v)
    total = int(round(v))
    days, rest = divmod(total, 86400)
    hours, rest = divmod(rest, 3600)
    minutes, seconds = divmod(rest, 60)
    parts = [(days, "d"), (hours, "h"), (minutes, "min"), (seconds, "s")]
    while parts and parts[-1][0] == 0:
        parts.pop()   # drop trailing zero parts: 3600 -> "1 h"
    while parts[0][0] == 0:
        parts.pop(0)  # drop leading zero parts
    return " ".join(("%d %s" if i == 0 else "%02d %s") % p for i, p in enumerate(parts))


def humanize(value, kind="bytes", decimals=1):
    """Pure function. Turns a number into a short readable text. A minus sign is kept."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("value must be an ordinary number, got %r" % (value,))
    if kind not in KINDS:
        raise ValueError("kind must be one of: %s (got %r)" % (", ".join(KINDS), kind))
    if isinstance(decimals, bool) or not isinstance(decimals, int) or not 0 <= decimals <= 4:
        raise ValueError("decimals must be a whole number from 0 to 4, got %r" % (decimals,))
    v = abs(float(value))
    if kind == "bytes":
        v, i = _scale(v, 1024.0, _BYTE_UNITS, decimals)
        text = ("%d B" % round(v)) if i == 0 else ("%.*f %s" % (decimals, v, _BYTE_UNITS[i]))
    elif kind == "seconds":
        text = _duration(v, decimals)
    else:
        v, i = _scale(v, 1000.0, _COUNT_UNITS, decimals)
        if i == 0:
            text = ("%d" % round(v)) if v == int(v) else ("%.*f" % (decimals, v))
        else:
            text = "%.*f %s" % (decimals, v, _COUNT_UNITS[i])
    return ("-" + text) if value < 0 and any(ch in "123456789" for ch in text) else text


class SYHumanizeNumber:
    DESCRIPTION = ("Shows a big raw number the way people read it: file sizes (1.5 GB), durations (1 h 02 min 05 s) "
                   "or counts (12.3 k).")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {"default": 0.0, "min": -1e15, "max": 1e15, "step": 1.0, "tooltip": "The raw number to show."}),
                "kind": (KINDS, {"default": "bytes", "tooltip": "What the number counts: bytes of a file, seconds of time, or plain things."}),
                "decimals": ("INT", {"default": 1, "min": 0, "max": 4, "tooltip": "How many digits after the dot for big numbers."}),
            },
        }

    def run(self, value, kind="bytes", decimals=1):
        return (humanize(value, kind, int(decimals)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "HumanizeNumber", SYHumanizeNumber)
NODE_DISPLAY_NAME_MAPPINGS["SYHumanizeNumber"] = "Humanize Number SY"
