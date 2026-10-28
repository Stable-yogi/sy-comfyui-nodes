"""Frame Range Info SY: lists the frame numbers of a start, end and step."""
try:
    from ._sy_common import category, register
    from ._sy_videoframes import frame_range
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_videoframes import frame_range


def range_info(start, end, step):
    """Returns (list_text, count, last_frame)."""
    nums = frame_range(start, end, step)
    return (", ".join(str(n) for n in nums), len(nums), nums[-1])


class SYFrameRangeInfo:
    DESCRIPTION = "Shows which frame numbers a start, end and step pick, and how many. The end counts when a step lands on it."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("list", "count", "last")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "start": ("INT", {"default": 0, "min": 0, "max": 1000000, "tooltip": "First frame number."}),
                "end": ("INT", {"default": 80, "min": 0, "max": 1000000, "tooltip": "Last frame number. A smaller number than start counts down."}),
                "step": ("INT", {"default": 1, "min": 1, "max": 1000000, "tooltip": "Gap between frame numbers. 2 takes every second frame."}),
            }
        }

    def run(self, start, end, step):
        return range_info(start, end, step)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FrameRangeInfo", SYFrameRangeInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYFrameRangeInfo"] = "Frame Range Info SY"
