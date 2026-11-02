"""Glitch Slices SY: digital glitch look. Random strips slide sideways and red and blue slide a little differently."""
import random

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def check_settings(slices, max_shift, channel_split):
    if not 1 <= int(slices) <= 60:
        raise ValueError("slices must be between 1 and 60, got %r" % (slices,))
    if not 0.0 <= float(max_shift) <= 0.3:
        raise ValueError("max_shift must be between 0 and 0.3 (share of the width), got %r" % (max_shift,))
    if not 0.0 <= float(channel_split) <= 0.05:
        raise ValueError("channel_split must be between 0 and 0.05 (share of the width), got %r" % (channel_split,))


def plan_slices(height, slices, max_shift, seed):
    """Pure function. Cuts the picture height into strips and gives each a sideways shift.

    max_shift is in pixels here. Returns a list of (top, bottom, shift_in_pixels), top to bottom,
    covering every row once. The same seed always gives the same plan. More slices than rows are capped.
    """
    if height < 1:
        raise ValueError("height must be at least 1, got %r" % (height,))
    if slices < 1:
        raise ValueError("slices must be at least 1, got %r" % (slices,))
    if max_shift < 0:
        raise ValueError("max_shift must not be negative, got %r" % (max_shift,))
    slices = min(int(slices), int(height))
    rng = random.Random(int(seed))
    cuts = sorted(rng.sample(range(1, int(height)), slices - 1)) if slices > 1 else []
    edges = [0] + cuts + [int(height)]
    limit = int(round(max_shift))
    return [(edges[i], edges[i + 1], rng.randint(-limit, limit)) for i in range(len(edges) - 1)]


def glitch_tensor(image, slices, max_shift, channel_split, seed):
    """Torch. image [B,H,W,C] float 0..1 -> new tensor of the same shape. Frame k uses seed + k."""
    import torch

    check_settings(slices, max_shift, channel_split)
    out = image.clone()
    height, width, channels = image.shape[1], image.shape[2], image.shape[3]
    px_shift = max_shift * width
    split = int(round(float(channel_split) * width))
    for b in range(image.shape[0]):
        for top, bottom, shift in plan_slices(height, slices, px_shift, int(seed) + b):
            strip = image[b, top:bottom]
            if split == 0 or channels < 3:
                out[b, top:bottom] = torch.roll(strip, shifts=shift, dims=1)
                continue
            rolled = torch.roll(strip, shifts=shift, dims=1).clone()
            rolled[..., 0] = torch.roll(strip[..., 0], shifts=shift + split, dims=1)
            rolled[..., 2] = torch.roll(strip[..., 2], shifts=shift - split, dims=1)
            out[b, top:bottom] = rolled
    return out


class SYGlitchSlices:
    DESCRIPTION = ("Digital glitch look. Random horizontal strips of the picture slide sideways, and the red and blue "
                   "colours slide a little differently. The same seed gives the same glitch.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture (or batch of frames) to glitch. Each frame gets its own pattern."}),
            "slices": ("INT", {"default": 12, "min": 1, "max": 60, "tooltip": "How many horizontal strips the picture is cut into."}),
            "max_shift": ("FLOAT", {"default": 0.06, "min": 0.0, "max": 0.3, "step": 0.005, "tooltip": "Biggest sideways slide of a strip, as a share of the picture width."}),
            "channel_split": ("FLOAT", {"default": 0.01, "min": 0.0, "max": 0.05, "step": 0.001, "tooltip": "How far red and blue slide apart, as a share of the picture width."}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 53, "tooltip": "Same seed gives the same glitch. Change it for a new pattern."}),
        }}

    def run(self, image, slices, max_shift, channel_split, seed):
        return (glitch_tensor(image, slices, max_shift, channel_split, seed),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "GlitchSlices", SYGlitchSlices)
NODE_DISPLAY_NAME_MAPPINGS["SYGlitchSlices"] = "Glitch Slices SY"
