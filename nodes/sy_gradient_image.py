"""Gradient Image SY: makes a new picture that fades from one colour to another."""
import math

try:
    from ._sy_common import category, register
    from ._sy_hexcolour import parse_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_hexcolour import parse_hex

SHAPES = ("linear", "radial")
DEFAULT_A = "#" + "1b1b2f"
DEFAULT_B = "#" + "f5d58a"


def check_size(w, h):
    if w < 1 or h < 1:
        raise ValueError("width and height must be at least 1, got %sx%s" % (w, h))


def check_shape(shape):
    if shape not in SHAPES:
        raise ValueError("shape must be one of: %s, got %r" % (", ".join(SHAPES), shape))


def gradient_t(x, y, w, h, shape, angle):
    """Pure function. Position 0..1 along the gradient for pixel (x, y) in a w x h picture (pixel centre used).
    linear: angle 0 runs left to right, 90 top to bottom, measured over the full rotated extent of the rectangle.
    radial: distance from the centre divided by the centre-to-corner distance."""
    check_size(w, h)
    check_shape(shape)
    px, py = x + 0.5 - w / 2.0, y + 0.5 - h / 2.0
    if shape == "radial":
        corner = math.hypot(w / 2.0, h / 2.0)
        t = math.hypot(px, py) / corner
    else:
        a = math.radians(angle)
        dx, dy = math.cos(a), math.sin(a)
        half = abs(dx) * w / 2.0 + abs(dy) * h / 2.0
        t = (px * dx + py * dy + half) / (2.0 * half)
    return 0.0 if t < 0.0 else 1.0 if t > 1.0 else t


def gradient_pixel(t, a, b):
    return tuple(a[i] + t * (b[i] - a[i]) for i in range(3))


class SYGradientImage:
    DESCRIPTION = "Makes a new picture that fades from one colour to another, in a straight line or from the centre outward."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 1, "max": 8192, "step": 1, "tooltip": "Width of the new picture in pixels."}),
                "height": ("INT", {"default": 1024, "min": 1, "max": 8192, "step": 1, "tooltip": "Height of the new picture in pixels."}),
                "shape": (list(SHAPES), {"default": "linear", "tooltip": "linear fades along a line; radial fades from the centre to the corners."}),
                "colour_a": ("STRING", {"default": DEFAULT_A, "multiline": False, "tooltip": "Starting colour, as 3 or 6 hex digits like a web colour."}),
                "colour_b": ("STRING", {"default": DEFAULT_B, "multiline": False, "tooltip": "Ending colour, as 3 or 6 hex digits like a web colour."}),
                "angle": ("FLOAT", {"default": 0.0, "min": -360.0, "max": 360.0, "step": 1.0, "tooltip": "Linear only. 0 goes left to right, 90 goes top to bottom."}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1, "tooltip": "How many identical pictures to make."}),
            }
        }

    def run(self, width, height, shape, colour_a, colour_b, angle, batch_size):
        import torch

        check_size(width, height)
        check_shape(shape)
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1, got %s" % batch_size)
        a = parse_hex(colour_a, "colour_a")
        b = parse_hex(colour_b, "colour_b")
        py = (torch.arange(height, dtype=torch.float32) + 0.5 - height / 2.0)[:, None]
        px = (torch.arange(width, dtype=torch.float32) + 0.5 - width / 2.0)[None, :]
        if shape == "radial":
            t = torch.sqrt(px * px + py * py) / math.hypot(width / 2.0, height / 2.0)
        else:
            r = math.radians(angle)
            dx, dy = math.cos(r), math.sin(r)
            half = abs(dx) * width / 2.0 + abs(dy) * height / 2.0
            t = (px * dx + py * dy + half) / (2.0 * half)
        t = t.clamp(0.0, 1.0)
        ca = torch.tensor(a, dtype=torch.float32)
        cb = torch.tensor(b, dtype=torch.float32)
        img = ca + t.unsqueeze(-1) * (cb - ca)
        img = img[None].repeat(batch_size, 1, 1, 1).contiguous()
        mask = t[None].repeat(batch_size, 1, 1).contiguous()
        return (img, mask)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "GradientImage", SYGradientImage)
NODE_DISPLAY_NAME_MAPPINGS["SYGradientImage"] = "Gradient Image SY"
