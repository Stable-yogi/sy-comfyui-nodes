"""XY Values List SY: builds the list of values for one axis of an XY plot."""
try:
    from ._sy_common import category, register
    from ._sy_xy import MODES, build_values, format_number, MAX_VALUES
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_xy import MODES, build_values, format_number, MAX_VALUES

SCALES = ["linear", "log"]
NL = chr(10)


def log_range(start, stop, steps):
    """Pure function. Numbers spaced by the same factor (1, 2, 4, 8 ...) from start to stop. Both must be above 0."""
    steps = int(steps)
    start, stop = float(start), float(stop)
    if steps < 1 or steps > MAX_VALUES:
        raise ValueError("steps must be between 1 and %d, got %d" % (MAX_VALUES, steps))
    if not (start > 0 and stop > 0):
        raise ValueError("log scale needs start and stop above 0, got %s and %s. Use linear for zero or negative numbers" % (format_number(start), format_number(stop)))
    if steps == 1:
        return [format_number(start)]
    return [format_number(start * (stop / start) ** (i / (steps - 1))) for i in range(steps)]


def make_list_ex(mode, start, stop, steps, text, seed_first, seed_count, seed_step, scale="linear", whole_numbers=False, remove_duplicates=False):
    """Pure function. Returns (newline text, count, info). Extra choices: log spacing, whole numbers, drop repeated values."""
    if scale not in SCALES:
        raise ValueError("scale must be one of: %s" % ", ".join(SCALES))
    if mode == "numbers" and scale == "log":
        vals = log_range(start, stop, steps)
    else:
        vals = build_values(mode, start, stop, steps, text, seed_first, seed_count, seed_step)
    notes = []
    if whole_numbers and mode == "numbers":
        vals = [format_number(round(float(v))) for v in vals]
        notes.append("rounded to whole numbers")
        remove_duplicates = True
    removed = 0
    if remove_duplicates:
        seen, kept = set(), []
        for v in vals:
            key = v.lower()
            if key in seen:
                removed += 1
                continue
            seen.add(key)
            kept.append(v)
        vals = kept
        if removed:
            notes.append("%d repeated value%s removed" % (removed, "" if removed == 1 else "s"))
    spacing = {"numbers": "evenly spaced" if scale == "linear" else "log spaced"}.get(mode, "typed list" if mode == "text list" else "seeds")
    shown = ", ".join(vals) if len(vals) <= 8 else ", ".join(vals[:4]) + ", ... , " + ", ".join(vals[-2:])
    info = "%d value%s (%s): %s" % (len(vals), "" if len(vals) == 1 else "s", spacing, shown)
    if notes:
        info += ". " + ", ".join(notes).capitalize()
    return NL.join(vals), len(vals), info


def make_list(mode, start, stop, steps, text, seed_first, seed_count, seed_step):
    """Pure function. Returns (newline text, count)."""
    vals = build_values(mode, start, stop, steps, text, seed_first, seed_count, seed_step)
    return NL.join(vals), len(vals)


class SYXYValuesList:
    DESCRIPTION = ("Builds the list of values for one side of an XY plot: a number range, a typed list, or a run of seeds. "
                   "Numbers can be spaced evenly or by a factor (log), rounded to whole numbers (for steps), and repeated values can be dropped. "
                   "The info output shows what the list holds.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("values", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (list(MODES), {"default": "numbers", "tooltip": "numbers = a range, text list = values you type, seeds = a run of seed numbers."}),
                "start": ("FLOAT", {"default": 1.0, "min": -1000000.0, "max": 1000000.0, "step": 0.01, "tooltip": "First number of the range (numbers mode)."}),
                "stop": ("FLOAT", {"default": 8.0, "min": -1000000.0, "max": 1000000.0, "step": 0.01, "tooltip": "Last number of the range (numbers mode)."}),
                "steps": ("INT", {"default": 4, "min": 1, "max": 64, "tooltip": "How many numbers in the range, including first and last."}),
                "text": ("STRING", {"default": "euler, dpmpp_2m, ddim", "multiline": True, "tooltip": "Values separated by commas or new lines (text list mode)."}),
                "seed_first": ("INT", {"default": 0, "min": 0, "max": 2 ** 63 - 1, "tooltip": "First seed (seeds mode)."}),
                "seed_count": ("INT", {"default": 4, "min": 1, "max": 64, "tooltip": "How many seeds to make (seeds mode)."}),
                "seed_step": ("INT", {"default": 1, "min": -1000000, "max": 1000000, "tooltip": "Added to each seed to get the next one (seeds mode)."}),
            },
            "optional": {
                "scale": (SCALES, {"default": "linear", "tooltip": "numbers mode: linear = same distance between values, log = same factor (1, 2, 4, 8). Log needs numbers above 0."}),
                "whole_numbers": ("BOOLEAN", {"default": False, "tooltip": "numbers mode: round to whole numbers, good for steps. Repeated values are dropped."}),
                "remove_duplicates": ("BOOLEAN", {"default": False, "tooltip": "Drop values that appear twice, so no picture is rendered twice."}),
            },
        }

    def run(self, mode, start, stop, steps, text, seed_first, seed_count, seed_step, scale="linear", whole_numbers=False, remove_duplicates=False):
        return make_list_ex(mode, start, stop, steps, text, seed_first, seed_count, seed_step, scale, bool(whole_numbers), bool(remove_duplicates))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "XYValuesList", SYXYValuesList)
NODE_DISPLAY_NAME_MAPPINGS["SYXYValuesList"] = "XY Values List SY"
