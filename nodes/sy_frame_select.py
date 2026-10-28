"""Frame Select SY: takes a range of frames (start, end, step) from a batch. Negative numbers count from the end."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape


def resolve_index(value, total, name):
    """Pure function. Negative values count from the end (-1 is the last frame). Raises if outside the batch."""
    value, total = int(value), int(total)
    idx = value + total if value < 0 else value
    if idx < 0 or idx >= total:
        raise ValueError("%s %d is outside the batch of %d frames (allowed: %d to %d)" % (name, value, total, -total, total - 1))
    return idx


def select_indices(total, start, end, step):
    """Pure function. Frame numbers from start to end, both included, every `step` frames."""
    total, step = int(total), int(step)
    if total < 1:
        raise ValueError("batch is empty: need at least 1 frame, got %d" % total)
    if step < 1:
        raise ValueError("step must be at least 1, got %d" % step)
    s = resolve_index(start, total, "start")
    e = resolve_index(end, total, "end")
    if e < s:
        raise ValueError("end (frame %d) comes before start (frame %d): swap them or use Reverse Batch" % (e, s))
    return list(range(s, e + 1, step))


class SYFrameSelect:
    DESCRIPTION = "Takes some frames from a batch: from start to end (both included), every step frames. Negative numbers count from the end."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("images", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The batch of frames to take from."}),
                "start": ("INT", {"default": 0, "min": -100000, "max": 100000, "tooltip": "First frame to keep, counting from 0. -1 means the last frame."}),
                "end": ("INT", {"default": -1, "min": -100000, "max": 100000, "tooltip": "Last frame to keep, included. -1 means the last frame."}),
                "step": ("INT", {"default": 1, "min": 1, "max": 1000, "tooltip": "Keep every this many frames. 2 keeps every second frame."}),
            }
        }

    def run(self, images, start, end, step):
        check_shape(images.shape)
        ids = select_indices(images.shape[0], start, end, step)
        return (images[ids], len(ids))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FrameSelect", SYFrameSelect)
NODE_DISPLAY_NAME_MAPPINGS["SYFrameSelect"] = "Frame Select SY"
