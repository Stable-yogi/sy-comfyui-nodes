"""Shared picture helpers for the Image nodes. Pure maths on plain values; torch is imported only inside functions."""
import math

COLOURS = {
    "black": (0, 0, 0), "white": (255, 255, 255), "grey": (128, 128, 128),
    "red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255),
}
COLOUR_NAMES = tuple(COLOURS)
CUSTOM_TIP = "Optional own colour as red,green,blue numbers 0 to 255, for example 200,120,40. Empty uses the list."


def clamp01(v):
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def smoothstep(t):
    t = clamp01(t)
    return t * t * (3.0 - 2.0 * t)


def parse_colour(name, custom=""):
    """Returns (r, g, b) as floats 0..1. `custom` like 200,120,40 wins when it is not empty."""
    custom = (custom or "").strip()
    if custom:
        parts = [p.strip() for p in custom.split(",")]
        try:
            vals = [int(p) for p in parts]
        except ValueError:
            vals = []
        if len(vals) != 3 or any(v < 0 or v > 255 for v in vals):
            raise ValueError("custom colour must be three whole numbers from 0 to 255 separated by commas, got %r" % custom)
        return tuple(v / 255.0 for v in vals)
    if name not in COLOURS:
        raise ValueError("unknown colour %r, pick one of: %s" % (name, ", ".join(COLOUR_NAMES)))
    return tuple(v / 255.0 for v in COLOURS[name])


def gaussian_kernel(radius):
    """Normalised 1D gaussian weights (a list that sums to 1). sigma equals radius."""
    radius = float(radius)
    if radius <= 0:
        return [1.0]
    half = max(1, int(math.ceil(3.0 * radius)))
    w = [math.exp(-(i * i) / (2.0 * radius * radius)) for i in range(-half, half + 1)]
    s = sum(w)
    return [v / s for v in w]


def blur_1d(values, radius):
    """Pure blur of a plain list of numbers with edge clamping."""
    k = gaussian_kernel(radius)
    half = len(k) // 2
    n = len(values)
    return [sum(k[j] * values[min(n - 1, max(0, i + j - half))] for j in range(len(k))) for i in range(n)]


def need_image(img):
    if getattr(img, "ndim", 0) != 4:
        raise ValueError("expected a picture batch shaped [batch, height, width, channels]")


def blur_tensor(img, radius):
    """Gaussian blur of a [B,H,W,C] tensor, separable, edges repeated."""
    import torch
    import torch.nn.functional as F

    radius = float(radius)
    if radius <= 0:
        return img
    k = torch.tensor(gaussian_kernel(radius), dtype=img.dtype, device=img.device)
    half = k.numel() // 2
    c = img.shape[3]
    x = img.permute(0, 3, 1, 2)
    x = F.pad(x, (half, half, half, half), mode="replicate")
    x = F.conv2d(x, k.view(1, 1, 1, -1).repeat(c, 1, 1, 1), groups=c)
    x = F.conv2d(x, k.view(1, 1, -1, 1).repeat(c, 1, 1, 1), groups=c)
    return x.permute(0, 2, 3, 1).contiguous()


def resize_tensor(img, height, width, interpolation="bilinear"):
    """Resize [B,H,W,C] to a new size. interpolation: nearest-exact, bilinear, bicubic, area."""
    import torch.nn.functional as F

    if interpolation not in ("nearest-exact", "bilinear", "bicubic", "area"):
        raise ValueError("unknown interpolation %r" % (interpolation,))
    if img.shape[1] == height and img.shape[2] == width:
        return img
    x = img.permute(0, 3, 1, 2)
    kw = {}
    if interpolation in ("bilinear", "bicubic"):
        kw = {"align_corners": False, "antialias": True}
    x = F.interpolate(x, size=(int(height), int(width)), mode=interpolation, **kw)
    return x.permute(0, 2, 3, 1).clamp(0.0, 1.0).contiguous()
