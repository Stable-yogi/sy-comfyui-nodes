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


def parse_numbers_lenient(text):
    """Pure function. Like parse_numbers but skips pieces that are not numbers. Returns (values, skipped pieces)."""
    pieces = [p for p in re.split(r"[,\s]+", text or "") if p]
    out, skipped = [], []
    for p in pieces:
        try:
            v = float(p)
        except ValueError:
            skipped.append(p)
            continue
        if math.isfinite(v):
            out.append(v)
        else:
            skipped.append(p)
    if not out:
        raise ValueError("numbers has no usable number at all; type some numbers separated by commas, spaces or new lines")
    return out, skipped


def stats_extras(values, skipped=()):
    """Pure function. Returns (stdev, sorted_text, info). stdev is the spread of the whole list (population)."""
    n = len(values)
    mean = math.fsum(values) / n
    stdev = math.sqrt(math.fsum((v - mean) ** 2 for v in values) / n)
    sorted_text = ", ".join("%g" % v for v in sorted(values))
    info = "%d numbers read" % n
    if skipped:
        shown = ", ".join(skipped[:5]) + (" ..." if len(skipped) > 5 else "")
        info += ", %d skipped because they are not numbers (%s)" % (len(skipped), shown)
    return stdev, sorted_text, info


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
    DESCRIPTION = "Reads a list of numbers and gives the count, sum, average, middle value, smallest and largest, plus the spread (stdev) and the sorted list. With ignore_bad on, pieces like 5px are skipped and listed in the info line instead of stopping the run."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "STRING", "FLOAT", "STRING", "STRING")
    RETURN_NAMES = ("count", "sum", "mean", "median", "min", "max", "summary", "stdev", "sorted_list", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "numbers": ("STRING", {"multiline": True, "default": "1, 2, 3", "tooltip": "Numbers separated by commas, spaces or new lines."}),
            },
            "optional": {
                "ignore_bad": ("BOOLEAN", {"default": False, "tooltip": "On skips pieces that are not numbers (like 5px) and says so in info. Off refuses them."}),
            },
        }

    def run(self, numbers, ignore_bad=False):
        if ignore_bad:
            values, skipped = parse_numbers_lenient(numbers)
        else:
            values, skipped = parse_numbers(numbers), []
        s = list_stats(values)
        stdev, sorted_text, info = stats_extras(values, skipped)
        return (s["count"], s["sum"], s["mean"], s["median"], s["min"], s["max"], s["summary"], stdev, sorted_text, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ListStats", SYListStats)
NODE_DISPLAY_NAME_MAPPINGS["SYListStats"] = "List Stats SY"
