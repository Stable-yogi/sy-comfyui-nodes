"""Frame Range Info SY: lists the frame numbers of a start, end and step."""
try:
    from ._sy_common import category, register
    from ._sy_videoframes import frame_range
    from ._sy_a1_sizes import FRAME_RULES, snap_frame_count, is_4n1
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_videoframes import frame_range
    from _sy_a1_sizes import FRAME_RULES, snap_frame_count, is_4n1


def range_info(start, end, step):
    """Returns (list_text, count, last_frame)."""
    nums = frame_range(start, end, step)
    return (", ".join(str(n) for n in nums), len(nums), nums[-1])


def plan_range(start, end, step, fps=0.0, frame_rule="off"):
    """Pure function. Returns (list_text, count, last, seconds, info).

    frame_rule '4n+1 trim' or '4n+1 extend' changes the END so the frame count is 4n+1 (what Wan and LTX style video
    models want). fps above 0 gives the length in seconds; 0 leaves seconds at 0.
    """
    fps = float(fps)
    if not (0.0 <= fps <= 1000.0):
        raise ValueError("fps must be between 0 and 1000, got %s" % fps)
    start, end, step = int(start), int(end), int(step)
    nums = frame_range(start, end, step)
    notes = []
    if frame_rule not in FRAME_RULES:
        raise ValueError("frame_rule must be one of: %s, got %r" % (", ".join(FRAME_RULES), frame_rule))
    fitted = snap_frame_count(len(nums), frame_rule)
    if fitted != len(nums):
        sign = 1 if end >= start else -1
        new_end = start + sign * step * (fitted - 1)
        if new_end < 0:
            raise ValueError("cannot extend to %d frames: the numbers would go below 0. Raise start or lower step." % fitted)
        nums = frame_range(start, new_end, step)
        notes.append("Changed %d frames to %d (rule %s); the end is now %d." % (len(frame_range(start, end, step)), len(nums), frame_rule, new_end))
    count = len(nums)
    seconds = round(count / fps, 3) if fps > 0 else 0.0
    head = "%d frames, from %d to %d, step %d" % (count, nums[0], nums[-1], step)
    if fps > 0:
        head += ", %.3g s at %g fps" % (seconds, fps)
    head += "."
    if not is_4n1(count):
        notes.append("%d is not 4n+1 (like 49, 81, 121). Wan and LTX style video models may round it." % count)
    return (", ".join(str(n) for n in nums), count, nums[-1], seconds, " ".join([head] + notes))


class SYFrameRangeInfo:
    DESCRIPTION = ("Shows which frame numbers a start, end and step pick, and how many. The end counts when a step lands on it. "
                   "Optional fps gives the length in seconds. Optional frame_rule fits the end so the count is 4n+1 "
                   "(81 frames and so on) for Wan and LTX style video models. An info line says it all in words.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "INT", "FLOAT", "STRING")
    RETURN_NAMES = ("list", "count", "last", "seconds", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "start": ("INT", {"default": 0, "min": 0, "max": 1000000, "tooltip": "First frame number."}),
                "end": ("INT", {"default": 80, "min": 0, "max": 1000000, "tooltip": "Last frame number. A smaller number than start counts down."}),
                "step": ("INT", {"default": 1, "min": 1, "max": 1000000, "tooltip": "Gap between frame numbers. 2 takes every second frame."}),
            },
            "optional": {
                "fps": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1000.0, "step": 1.0, "tooltip": "0 = off. The frame rate, to also give the length in seconds."}),
                "frame_rule": (FRAME_RULES, {"default": "off", "tooltip": "off keeps the end. 4n+1 trim/extend moves the end so the count is 4n+1."}),
            },
        }

    def run(self, start, end, step, fps=0.0, frame_rule="off"):
        if frame_rule == "off" and not fps:
            return range_info(start, end, step) + plan_range(start, end, step)[3:]
        return plan_range(start, end, step, fps, frame_rule)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FrameRangeInfo", SYFrameRangeInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYFrameRangeInfo"] = "Frame Range Info SY"
