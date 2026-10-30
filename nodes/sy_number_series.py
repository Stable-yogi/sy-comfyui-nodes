"""Number Series SY: makes a list of evenly spaced numbers between two values."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def number_series(start, stop, count):
    """Pure function. count evenly spaced values from start to stop, both included."""
    if count < 2 or count > 1000:
        raise ValueError("count must be between 2 and 1000, got %s" % count)
    step = (stop - start) / (count - 1)
    vals = [start + step * i for i in range(count)]
    vals[-1] = float(stop)
    return vals


def format_series(values, decimals):
    """Pure function. Values rounded to decimals, joined with a comma and a space. Negative zero prints as 0."""
    if decimals < 0 or decimals > 8:
        raise ValueError("decimals must be between 0 and 8, got %s" % decimals)
    parts = []
    for v in values:
        r = round(v, decimals)
        if r == 0:
            r = 0.0
        s = "%.*f" % (decimals, r)
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        parts.append(s if s not in ("", "-0") else "0")
    return ", ".join(parts)


class SYNumberSeries:
    DESCRIPTION = "Makes a list of evenly spaced numbers from a start to a stop value, both included, as text and a count."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "start": ("FLOAT", {"default": 0.0, "min": -1e9, "max": 1e9, "step": 0.01, "tooltip": "The first number in the list."}),
                "stop": ("FLOAT", {"default": 1.0, "min": -1e9, "max": 1e9, "step": 0.01, "tooltip": "The last number in the list."}),
                "count": ("INT", {"default": 5, "min": 2, "max": 1000, "step": 1, "tooltip": "How many numbers to make, including the first and last."}),
                "decimals": ("INT", {"default": 3, "min": 0, "max": 8, "step": 1, "tooltip": "How many digits after the point to keep."}),
            }
        }

    def run(self, start, stop, count, decimals):
        vals = number_series(start, stop, count)
        return (format_series(vals, decimals), len(vals))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "NumberSeries", SYNumberSeries)
NODE_DISPLAY_NAME_MAPPINGS["SYNumberSeries"] = "Number Series SY"
