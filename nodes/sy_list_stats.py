"""List Stats SY: counts, adds and averages a list of numbers typed as text."""
import math
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def parse_numbers(text):
    """Pure function. Numbers separated by commas, spaces or new lines become a list of floats."""
    pieces = [p for p in re.split(r"[,\s]+", text or "") if p]
    if not pieces:
        raise ValueError("numbers is empty; type some numbers separated by commas, spaces or new lines")
    out = []
    for p in pieces:
        try:
            v = float(p)
        except ValueError:
            raise ValueError("numbers has a piece that is not a number: %r" % p)
        if not math.isfinite(v):
            raise ValueError("numbers has a piece that is not a usable number: %r" % p)
        out.append(v)
    return out


def list_stats(values):
    """Pure function. Returns a dict with count, sum, mean, median, min, max and summary."""
    if not values:
        raise ValueError("numbers is empty; type some numbers separated by commas, spaces or new lines")
    srt = sorted(values)
    n = len(srt)
    total = math.fsum(srt)
    mid = n // 2
    median = srt[mid] if n % 2 else (srt[mid - 1] + srt[mid]) / 2.0
    stats = {"count": n, "sum": total, "mean": total / n, "median": median, "min": srt[0], "max": srt[-1]}
    stats["summary"] = "count=%d sum=%.3f mean=%.3f median=%.3f min=%.3f max=%.3f" % (
        n, stats["sum"], stats["mean"], stats["median"], stats["min"], stats["max"])
    return stats


class SYListStats:
    DESCRIPTION = "Reads a list of numbers and gives the count, sum, average, middle value, smallest and largest."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "STRING")
    RETURN_NAMES = ("count", "sum", "mean", "median", "min", "max", "summary")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "numbers": ("STRING", {"multiline": True, "default": "1, 2, 3", "tooltip": "Numbers separated by commas, spaces or new lines."}),
            }
        }

    def run(self, numbers):
        s = list_stats(parse_numbers(numbers))
        return (s["count"], s["sum"], s["mean"], s["median"], s["min"], s["max"], s["summary"])


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ListStats", SYListStats)
NODE_DISPLAY_NAME_MAPPINGS["SYListStats"] = "List Stats SY"
