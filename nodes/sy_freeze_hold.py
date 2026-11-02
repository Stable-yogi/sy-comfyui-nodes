"""Freeze Hold SY: holds one frame still for a chosen time inside a clip, then carries on."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def freeze_plan(total, freeze_at, hold_frames, replace=False):
    """Pure function. Returns the list of source frame numbers for the output clip.
    replace=False: the held frame is repeated `hold_frames` extra times and the clip gets longer.
    replace=True: the held frame overwrites the next frames and the length stays the same.
    freeze_at is clamped to the last frame."""
    total = int(total)
    hold = int(hold_frames)
    if total < 1:
        raise ValueError("the clip is empty: it needs at least 1 frame, got %d" % total)
    if hold < 1:
        raise ValueError("hold_frames must be at least 1, got %d" % hold)
    f = min(max(int(freeze_at), 0), total - 1)
    if replace:
        return [f if f <= i < f + hold else i for i in range(total)]
    return list(range(0, f + 1)) + [f] * hold + list(range(f + 1, total))


class SYFreezeHold:
    DESCRIPTION = ("Holds one frame still for a while inside a clip, then carries on. "
                   "Either adds extra frames (the clip gets longer) or overwrites the next frames (same length).")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("images", "new_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames of the clip, in order."}),
                "freeze_at": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Frame to hold, counting from 0. A number past the end uses the last frame."}),
                "hold_frames": ("INT", {"default": 24, "min": 1, "max": 1000, "tooltip": "How many frames the picture stays still."}),
                "replace": ("BOOLEAN", {"default": False, "tooltip": "Off: add extra frames. On: overwrite the following frames so the length stays."}),
            },
        }

    def run(self, images, freeze_at, hold_frames, replace=False):
        ids = freeze_plan(images.shape[0], freeze_at, hold_frames, replace)
        return (images[ids], len(ids))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FreezeHold", SYFreezeHold)
NODE_DISPLAY_NAME_MAPPINGS["SYFreezeHold"] = "Freeze Hold SY"
