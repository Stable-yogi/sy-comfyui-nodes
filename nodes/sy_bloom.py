"""Bloom SY: a soft glow from the bright parts of a picture."""
try:
    from ._sy_common import category, register
    from ._sy_hexcolour import parse_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_hexcolour import parse_hex

KNEE = 0.1  # how soft the edge of the threshold is


def bright_weight(value, threshold):
    """Pure function. 0..1: how much of a pixel of brightness `value` (0..1) feeds the glow.
    Fully off a little below the threshold, fully on a little above, smooth in between."""
    if not (0.0 <= threshold <= 1.0):
        raise ValueError("threshold must be between 0 and 1, got %s" % threshold)
    lo, hi = threshold - KNEE, threshold + KNEE
    t = (float(value) - lo) / (hi - lo)
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def gaussian_weights(radius):
    """Pure function. Normalised 1-D blur weights; sigma is half the radius. Length is 2*radius+1."""
    if radius < 1:
        raise ValueError("radius must be at least 1, got %s" % radius)
    r = int(radius)
    sigma = max(0.5, r / 2.0)
    w = [pow(2.718281828459045, -(i * i) / (2.0 * sigma * sigma)) for i in range(-r, r + 1)]
    total = sum(w)
    return [v / total for v in w]


def blur_nchw(x, radius):
    """Torch. Separable gaussian blur of [B,C,H,W] with edge-copy padding."""
    import torch
    import torch.nn.functional as F

    k = torch.tensor(gaussian_weights(radius), dtype=x.dtype, device=x.device)
    c = x.shape[1]
    r = int(radius)
    kh = k.view(1, 1, 1, -1).repeat(c, 1, 1, 1)
    kv = k.view(1, 1, -1, 1).repeat(c, 1, 1, 1)
    x = F.conv2d(F.pad(x, (r, r, 0, 0), mode="replicate"), kh, groups=c)
    return F.conv2d(F.pad(x, (0, 0, r, r), mode="replicate"), kv, groups=c)


def bloom_tensor(image, threshold, radius, strength, tint):
    """Torch [B,H,W,C]. Colour channels only; alpha and extra channels stay."""
    import torch

    if not (0.0 <= threshold <= 1.0):
        raise ValueError("threshold must be between 0 and 1, got %s" % threshold)
    if int(radius) < 1:
        raise ValueError("radius must be at least 1, got %s" % radius)
    if strength < 0:
        raise ValueError("strength cannot be negative, got %s" % strength)
    tint_rgb = parse_hex(tint, "tint")
    if strength == 0 or image.shape[3] < 3:
        return image
    rgb = image[..., :3].float()
    peak = rgb.amax(dim=-1, keepdim=True)
    lo, hi = threshold - KNEE, threshold + KNEE
    t = ((peak - lo) / (hi - lo)).clamp(0.0, 1.0)
    weight = t * t * (3.0 - 2.0 * t)
    glow = blur_nchw((rgb * weight).permute(0, 3, 1, 2), int(radius)).permute(0, 2, 3, 1)
    glow = glow * torch.tensor(tint_rgb, dtype=glow.dtype, device=glow.device) * float(strength)
    glow = glow.clamp(0.0, 1.0)
    screen = 1.0 - (1.0 - rgb) * (1.0 - glow)
    out = image.clone()
    out[..., :3] = screen.clamp(0.0, 1.0).to(image.dtype)
    return out


class SYBloom:
    DESCRIPTION = ("Adds a soft glow around the bright parts of a picture: the bright parts are blurred, tinted "
                   "and laid back on top. Strength 0 leaves the picture as it is.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to add a glow to."}),
            "threshold": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Only parts brighter than this glow. Lower makes more of the picture glow."}),
            "radius": ("INT", {"default": 24, "min": 1, "max": 200, "tooltip": "How far the glow spreads, in pixels."}),
            "strength": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 2.0, "step": 0.01, "tooltip": "How strong the glow is. 0 does nothing."}),
            "tint": ("STRING", {"default": "#fff", "tooltip": "Colour of the glow as a web colour, like #fff for white or #fb6 for warm."}),
        }}

    def run(self, image, threshold, radius, strength, tint):
        return (bloom_tensor(image, threshold, radius, strength, tint),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Bloom", SYBloom)
