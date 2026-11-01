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


ALLOWED_CODES = set("aAbBdHIjmMpSUwWyYzZ%")
_UNSAFE = set('<>:"/|?*') | {chr(92)}


def format_custom(value, pattern, use_utc=False, filename_safe=True):
    """Pure function. Your own pattern with % codes, for example %Y%m%d_%H%M -> 20260101_0930.

    Allowed codes: %Y %y %m %d %H %I %M %S %p %j %a %A %b %B %w %U %W %z %Z %%. With filename_safe, characters that
    cannot be in a file name (: / and so on) become a dash.
    """
    pattern = str(pattern)
    if not pattern.strip():
        raise ValueError("custom format is empty: type a pattern such as %Y-%m-%d_%H-%M")
    i = 0
    while i < len(pattern):
        if pattern[i] == "%":
            code = pattern[i + 1:i + 2]
            if code not in ALLOWED_CODES or code == "":
                raise ValueError("custom format has an unknown code %%%s. Allowed: %s" % (code, " ".join("%" + c for c in sorted(ALLOWED_CODES - {"%"}))))
            i += 2
        else:
            i += 1
    parts = time.gmtime(float(value)) if use_utc else time.localtime(float(value))
    text = time.strftime(pattern, parts)
    if filename_safe:
        text = "".join("-" if c in _UNSAFE or ord(c) < 32 else c for c in text)
    return text


def zone_text(value, use_utc=False):
    """Pure function. 'UTC' or 'UTC+01:00': the clock the text was made with."""
    if use_utc:
        return "UTC"
    off = getattr(time.localtime(float(value)), "tm_gmtoff", None)
    if off is None:
        return "local time"
    sign = "+" if off >= 0 else "-"
    off = abs(int(off))
    return "UTC%s%02d:%02d" % (sign, off // 3600, off % 3600 // 60)


class SYTimestamp:
    DESCRIPTION = ("Gives the current date and time as text. Handy for file names, folders and notes. "
                   "Type your own pattern (for example %Y%m%d_%H%M) to get exactly the look you want. "
                   "Also gives the unix seconds as a number and an info line saying which clock was used.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("timestamp", "unix_seconds", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "format": (list(FORMATS), {"default": "date_time", "tooltip": "Which look the text has. Compact has no separators. Unix is seconds."}),
                "use_utc": ("BOOLEAN", {"default": False, "tooltip": "On: use world time (UTC). Off: use the clock of this computer."}),
            },
            "optional": {
                "custom_format": ("STRING", {"default": "", "tooltip": "Your own pattern, for example %Y%m%d_%H%M. Empty uses the format above."}),
                "filename_safe": ("BOOLEAN", {"default": True, "tooltip": "For the custom pattern: turn characters that cannot be in a file name (: / and so on) into dashes."}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        return float("nan")

    def run(self, format, use_utc=False, custom_format="", filename_safe=True):
        now = time.time()
        if str(custom_format).strip():
            text = format_custom(now, custom_format, bool(use_utc), bool(filename_safe))
            how = "custom pattern"
        else:
            text = format_time(now, format, bool(use_utc))
            how = "format " + format
        return (text, int(now), "%s (%s, %s)" % (text, how, zone_text(now, bool(use_utc))))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Timestamp", SYTimestamp)
