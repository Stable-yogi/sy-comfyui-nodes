"""Batch Max Blend SY: keeps the brightest value at every pixel over all frames."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

OUTPUTS = ["last frame of trail", "every step"]


def decay_factor(decay):
    """Pure function. Multiplier applied to the old trail before each new frame."""
    decay = float(decay)
    if decay < 0.0 or decay > 1.0:
        raise ValueError("decay must be between 0 and 1 (got %s)" % decay)
    return 1.0 - decay


def used_range(total, start, count):
    """Pure function. Returns (first, last_exclusive) of the frames to use."""
    total, start, count = int(total), int(start), int(count)
    if total < 1:
        raise ValueError("the batch has no pictures")
    if start >= total:
        raise ValueError("start is %d but the batch only has %d pictures. Lower start" % (start, total))
    end = total if count == 0 else min(total, start + count)
    return start, end


class SYBatchMaxBlend:
    DESCRIPTION = ("Keeps the brightest value at every pixel over all frames: light trails, stars, sparks. "
                   "With decay above 0, older light fades. Frames are processed one at a time.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames of the clip, in order."}),
                "start": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "The first frame to use. 0 is the first frame of the clip."}),
                "count": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "How many frames to use. 0 means all frames to the end."}),
                "decay": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "0 = trails never fade. Higher = older light fades faster."}),
                "output": (OUTPUTS, {"default": "last frame of trail", "tooltip": "One finished picture, or the growing trail after every frame."}),
            }
        }

    def run(self, images, start, count, decay, output):
        import torch

        if output not in OUTPUTS:
            raise ValueError("output must be one of: %s (got %r)" % (", ".join(OUTPUTS), output))
        factor = decay_factor(decay)
        first, end = used_range(images.shape[0], start, count)
        every = output == "every step"
        result = torch.empty((end - first,) + tuple(images.shape[1:]), dtype=images.dtype) if every else None
        trail = None
        for k, i in enumerate(range(first, end)):
            frame = images[i]
            if trail is None:
                trail = frame.clone()
            else:
                if factor != 1.0:
                    trail = trail * factor
                trail = torch.maximum(trail, frame)
            if every:
                result[k] = trail
        if every:
            return (result,)
        return (trail.unsqueeze(0),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchMaxBlend", SYBatchMaxBlend)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchMaxBlend"] = "Batch Max Blend SY"
