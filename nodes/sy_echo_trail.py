"""Echo Trail SY: ghost trails. Each frame is mixed with the frames before it, fading with age."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ["average", "lighten"]


def echo_weights(echoes, decay):
    """Pure function. Weights for the newest frame first, then older ones. They add up to 1.
    Each older frame counts `decay` times as much as the one before it."""
    echoes = int(echoes)
    decay = float(decay)
    if echoes < 1 or echoes > 12:
        raise ValueError("echoes must be between 1 and 12, got %d" % echoes)
    if decay < 0.0 or decay > 1.0:
        raise ValueError("decay must be between 0 and 1, got %s" % decay)
    raw = [decay ** i for i in range(echoes)]
    total = sum(raw)
    return [w / total for w in raw]


def source_index(frame, age):
    """Pure function. Which input frame is `age` steps older than `frame`. The first frame is held at the start."""
    return max(int(frame) - int(age), 0)


class SYEchoTrail:
    DESCRIPTION = ("Makes ghost trails. Each frame is mixed with the frames before it, and older frames fade out, "
                   "so anything that moves leaves a trail behind it. A single picture comes back unchanged.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames of the clip, in order."}),
                "echoes": ("INT", {"default": 4, "min": 1, "max": 12, "tooltip": "How many earlier frames are mixed into each frame."}),
                "decay": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How much each older frame counts compared with the one after it. 0 = no trail."}),
                "mode": (MODES, {"default": "average", "tooltip": "Average blends the frames. Lighten keeps the brightest pixel, so bright things leave streaks."}),
            },
        }

    def run(self, images, echoes, decay, mode="average"):
        import torch
        if mode not in MODES:
            raise ValueError("mode must be one of: %s" % ", ".join(MODES))
        w = echo_weights(echoes, decay)
        n = images.shape[0]
        if n <= 1:
            return (images.clone(),)
        if mode == "average":
            out = torch.zeros_like(images)
            for age, wt in enumerate(w):
                idx = [source_index(t, age) for t in range(n)]
                out = out + images[idx] * wt
        else:
            out = images.clone()
            for age in range(1, len(w)):
                idx = [source_index(t, age) for t in range(n)]
                out = torch.maximum(out, images[idx] * (w[age] / w[0]))
        return (out.clamp(0.0, 1.0),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "EchoTrail", SYEchoTrail)
NODE_DISPLAY_NAME_MAPPINGS["SYEchoTrail"] = "Echo Trail SY"
