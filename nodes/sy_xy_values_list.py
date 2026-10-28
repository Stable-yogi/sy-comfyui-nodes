"""XY Values List SY: builds the list of values for one axis of an XY plot."""
try:
    from ._sy_common import category, register
    from ._sy_xy import MODES, build_values
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_xy import MODES, build_values


def make_list(mode, start, stop, steps, text, seed_first, seed_count, seed_step):
    """Pure function. Returns (newline text, count)."""
    vals = build_values(mode, start, stop, steps, text, seed_first, seed_count, seed_step)
    return "\n".join(vals), len(vals)


class SYXYValuesList:
    DESCRIPTION = "Builds the list of values for one side of an XY plot: a number range, a typed list, or a run of seeds."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("values", "count")

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
            }
        }

    def run(self, mode, start, stop, steps, text, seed_first, seed_count, seed_step):
        return make_list(mode, start, stop, steps, text, seed_first, seed_count, seed_step)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "XYValuesList", SYXYValuesList)
NODE_DISPLAY_NAME_MAPPINGS["SYXYValuesList"] = "XY Values List SY"
