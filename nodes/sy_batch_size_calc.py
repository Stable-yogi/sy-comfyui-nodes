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


class SYBatchSizeCalc:
    DESCRIPTION = ("Splits a total number of pictures into runs of at most a set size. "
                   "Gives the number of runs, the size of the last run and what is left over.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "INT")
    RETURN_NAMES = ("passes", "last_pass_size", "remainder")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "total": ("INT", {"default": 10, "min": 0, "max": MAX_TOTAL, "tooltip": "How many pictures you want in all."}),
                "max_per_pass": ("INT", {"default": 4, "min": 1, "max": 100000, "tooltip": "The most pictures one run can hold, such as what fits in memory."}),
            }
        }

    def run(self, total, max_per_pass):
        return calc_passes(total, max_per_pass)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchSizeCalc", SYBatchSizeCalc)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchSizeCalc"] = "Batch Size Calc SY"
