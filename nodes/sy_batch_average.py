"""Batch Average SY: averages all frames of a clip into one picture."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

WEIGHTINGS = ["even", "fade in", "fade out"]


def frame_weights(count, weighting="even"):
    """Pure function. Returns a list of `count` weights that add up to 1."""
    count = int(count)
    if count < 1:
        raise ValueError("need at least one frame to average (got %d)" % count)
    if weighting not in WEIGHTINGS:
        raise ValueError("weighting must be one of: %s (got %r)" % (", ".join(WEIGHTINGS), weighting))
    if weighting == "even":
        raw = [1.0] * count
    elif weighting == "fade in":
        raw = [float(i + 1) for i in range(count)]
    else:
        raw = [float(count - i) for i in range(count)]
    total = sum(raw)
    return [w / total for w in raw]


def used_range(total, start, count):
    """Pure function. Returns (first, last_exclusive) of the frames to use."""
    total, start, count = int(total), int(start), int(count)
    if total < 1:
        raise ValueError("the batch has no pictures")
    if start >= total:
        raise ValueError("start is %d but the batch only has %d pictures. Lower start" % (start, total))
    end = total if count == 0 else min(total, start + count)
    return start, end


class SYBatchAverage:
    DESCRIPTION = ("Averages the frames of a clip into one picture, like a long exposure. "
                   "It smooths away moving crowds and traffic. Frames are added one at a time, so long clips are fine.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames of the clip, in order."}),
                "start": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "The first frame to use. 0 is the first frame of the clip."}),
                "count": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "How many frames to average. 0 means all frames to the end."}),
                "weighting": (WEIGHTINGS, {"default": "even", "tooltip": "Even counts every frame the same. Fade in favours later frames, fade out earlier ones."}),
            }
        }

    def run(self, images, start, count, weighting):
        import torch

        first, end = used_range(images.shape[0], start, count)
        weights = frame_weights(end - first, weighting)
        total = None
        for k, i in enumerate(range(first, end)):
            frame = images[i].to(torch.float32)
            total = frame * weights[k] if total is None else total.add_(frame, alpha=weights[k])
        return (total.clamp(0.0, 1.0).unsqueeze(0).to(images.dtype),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchAverage", SYBatchAverage)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchAverage"] = "Batch Average SY"
