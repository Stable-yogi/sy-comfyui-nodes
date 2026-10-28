"""Timestamp SY: gives the current date and/or time as text, for file names and notes."""
import time

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

FORMATS = ("date", "time", "date_time", "compact", "unix")
_PATTERNS = {
    "date": "%Y-%m-%d",
    "time": "%H-%M-%S",
    "date_time": "%Y-%m-%d_%H-%M-%S",
    "compact": "%Y%m%d%H%M%S",
}


def format_time(value, fmt, use_utc=False):
    """Pure function. value = seconds since 1970 (like time.time()). Returns text."""
    if fmt not in FORMATS:
        raise ValueError("unknown timestamp format %r - pick one of: %s" % (fmt, ", ".join(FORMATS)))
    seconds = float(value)
    if fmt == "unix":
        return str(int(seconds))
    parts = time.gmtime(seconds) if use_utc else time.localtime(seconds)
    return time.strftime(_PATTERNS[fmt], parts)


class SYTimestamp:
    DESCRIPTION = "Gives the current date and time as text. Handy for file names, folders and notes."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("timestamp",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "format": (list(FORMATS), {"default": "date_time", "tooltip": "Which look the text has. Compact has no separators. Unix is seconds."}),
                "use_utc": ("BOOLEAN", {"default": False, "tooltip": "On: use world time (UTC). Off: use the clock of this computer."}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        return float("nan")

    def run(self, format, use_utc=False):
        return (format_time(time.time(), format, bool(use_utc)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Timestamp", SYTimestamp)
