"""Batch Size Calc SY: split a total number of images into passes of a maximum size."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_TOTAL = 10_000_000


def calc_passes(total, max_per_pass):
    """Pure function. Returns (passes, last_pass_size, remainder).

    passes = how many runs are needed. last_pass_size = images in the final run (0 when total is 0).
    remainder = total % max_per_pass (0 means every run is full).
    """
    total, max_per_pass = int(total), int(max_per_pass)
    if total < 0:
        raise ValueError("total cannot be negative, got %d" % total)
    if total > MAX_TOTAL:
        raise ValueError("total must be at most %d, got %d" % (MAX_TOTAL, total))
    if max_per_pass < 1:
        raise ValueError("max_per_pass must be at least 1, got %d" % max_per_pass)
    if total == 0:
        return (0, 0, 0)
    passes = -(-total // max_per_pass)
    remainder = total % max_per_pass
    last = remainder if remainder else min(total, max_per_pass)
    return (passes, last, remainder)


def pass_sizes_text(total, max_per_pass):
    """Pure function. '4 + 4 + 2' for 10 in passes of 4. Long plans are shortened: '3333333 runs of 3, then 1'."""
    passes, last, _ = calc_passes(total, max_per_pass)
    if passes == 0:
        return "no runs (nothing to do)"
    full = passes - 1 if last < min(total, max_per_pass) else passes
    size = min(total, max_per_pass)
    if passes <= 12:
        return " + ".join([str(size)] * full + ([str(last)] if full < passes else []))
    text = "%d runs of %d" % (full, size)
    return text + (", then 1 run of %d" % last if full < passes else "")


def batch_info(total, max_per_pass):
    """Pure function. Returns (pass_size, info). pass_size = pictures in a normal (full) run."""
    passes, last, rem = calc_passes(total, max_per_pass)
    if passes == 0:
        return 0, "Total is 0: nothing to render."
    size = min(int(total), int(max_per_pass))
    head = "%d pictures, at most %d per run -> %d run%s: %s." % (int(total), int(max_per_pass), passes, "" if passes == 1 else "s", pass_sizes_text(total, max_per_pass))
    if int(total) <= int(max_per_pass):
        head += " Everything fits in one run."
    elif rem:
        head += " The last run is shorter (%d)." % last
    else:
        head += " Every run is full."
    return size, head


class SYBatchSizeCalc:
    DESCRIPTION = ("Splits a total number of pictures into runs of at most a set size. "
                   "Gives the number of runs, the size of the last run and what is left over. "
                   "Adds the size of a normal run and a plain text such as '10 pictures, at most 4 per run -> 3 runs: 4 + 4 + 2'.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("passes", "last_pass_size", "remainder", "pass_size", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "total": ("INT", {"default": 10, "min": 0, "max": MAX_TOTAL, "tooltip": "How many pictures you want in all."}),
                "max_per_pass": ("INT", {"default": 4, "min": 1, "max": 100000, "tooltip": "The most pictures one run can hold, such as what fits in memory."}),
            }
        }

    def run(self, total, max_per_pass):
        size, info = batch_info(total, max_per_pass)
        return calc_passes(total, max_per_pass) + (size, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchSizeCalc", SYBatchSizeCalc)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchSizeCalc"] = "Batch Size Calc SY"
