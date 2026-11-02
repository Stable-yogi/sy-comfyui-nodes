"""Mask Shape Draw SY: draws a mask (rectangle, ellipse, gradient) from numbers."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

SHAPES = ("rectangle", "ellipse", "rounded rectangle", "linear gradient", "radial gradient")


class _PyOps:
    """Plain-number versions of the few maths helpers the shape code needs."""
    sqrt = staticmethod(math.sqrt)
    abs = staticmethod(abs)

    @staticmethod
    def maxv(a, b):
        return max(a, b)

    @staticmethod
    def minv(a, b):
        return min(a, b)

    @staticmethod
    def clamp01(a):
        return min(1.0, max(0.0, a))


def _smooth(t):
    return t * t * (3.0 - 2.0 * t)


def default_params(width=1, height=1):
    return {"width": width, "height": height, "cx": 0.5, "cy": 0.5, "sx": 0.5, "sy": 0.5,
            "feather": 0.0, "angle": 0.0}


def check_args(width, height, shape):
    """Pure function. Raises ValueError with a plain message for bad settings."""
    if int(width) < 8 or int(width) > 8192 or int(height) < 8 or int(height) > 8192:
        raise ValueError("width and height must each be between 8 and 8192, got %sx%s" % (width, height))
    if shape not in SHAPES:
        raise ValueError("shape must be one of %s, got %r" % (", ".join(SHAPES), shape))


def _shape_core(shape, u, v, p, ops):
    """One piece of logic for numbers and tensors. u, v are 0..1 across the picture."""
    w = float(p["width"])
    h = float(p["height"])
    x0 = (u - p["cx"]) * w
    y0 = (v - p["cy"]) * h
    a = math.radians(p["angle"])
    ca, sa = math.cos(a), math.sin(a)
    x = x0 * ca + y0 * sa
    y = y0 * ca - x0 * sa
    hx = max(1e-6, p["sx"] * w / 2.0)
    hy = max(1e-6, p["sy"] * h / 2.0)
    f = p["feather"] * min(w, h)

    if shape in ("linear gradient", "radial gradient"):
        if shape == "linear gradient":
            t = ops.clamp01(0.5 + x / (2.0 * hx))
        else:
            t = 1.0 - ops.clamp01(ops.sqrt((x / hx) * (x / hx) + (y / hy) * (y / hy)))
        if f > 0:
            t = _smooth(t)
        return t

    if shape == "ellipse":
        k = ops.sqrt((x / hx) * (x / hx) + (y / hy) * (y / hy))
        sd = (k - 1.0) * min(hx, hy)
    else:
        r = 0.5 * min(hx, hy) if shape == "rounded rectangle" else 0.0
        qx = ops.abs(x) - hx + r
        qy = ops.abs(y) - hy + r
        outer = ops.sqrt(ops.maxv(qx, 0.0) * ops.maxv(qx, 0.0) + ops.maxv(qy, 0.0) * ops.maxv(qy, 0.0))
        sd = outer + ops.minv(ops.maxv(qx, qy), 0.0) - r
    if f > 0:
        return _smooth(ops.clamp01(0.5 - sd / (2.0 * f)))
    return ops.clamp01(0.5 - sd)


def shape_value(shape, u, v, params):
    """Pure function. Mask value 0..1 at the point (u, v), both 0..1 across the picture.

    params: width, height (pixels), cx, cy, sx, sy, feather, angle (see default_params).
    """
    if shape not in SHAPES:
        raise ValueError("shape must be one of %s, got %r" % (", ".join(SHAPES), shape))
    p = default_params()
    p.update(params)
    return _shape_core(shape, float(u), float(v), p, _PyOps)


def draw_mask(width, height, shape, centre_x, centre_y, size_x, size_y, feather, angle, invert):
    """Torch function. Returns a mask [1,H,W]."""
    import torch
    check_args(width, height, shape)
    w, h = int(width), int(height)

    class Ops:
        sqrt = staticmethod(torch.sqrt)
        abs = staticmethod(torch.abs)

        @staticmethod
        def maxv(a, b):
            if isinstance(b, (int, float)):
                return torch.clamp(a, min=b)
            return torch.maximum(a, b)

        @staticmethod
        def minv(a, b):
            if isinstance(b, (int, float)):
                return torch.clamp(a, max=b)
            return torch.minimum(a, b)

        @staticmethod
        def clamp01(a):
            return torch.clamp(a, 0.0, 1.0)

    u = ((torch.arange(w, dtype=torch.float32) + 0.5) / w).view(1, w).expand(h, w)
    v = ((torch.arange(h, dtype=torch.float32) + 0.5) / h).view(h, 1).expand(h, w)
    p = {"width": w, "height": h, "cx": float(centre_x), "cy": float(centre_y), "sx": float(size_x),
         "sy": float(size_y), "feather": float(feather), "angle": float(angle)}
    out = _shape_core(shape, u, v, p, Ops)
    if invert:
        out = 1.0 - out
    return out.clamp(0.0, 1.0).unsqueeze(0).contiguous()


class SYMaskShapeDraw:
    DESCRIPTION = ("Draws a mask from numbers: rectangle, ellipse, rounded rectangle, or a linear or radial gradient. "
                   "Set the size and place, soften the edge, rotate it, or flip it.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 8, "max": 8192, "tooltip": "Width of the mask in pixels."}),
                "height": ("INT", {"default": 1024, "min": 8, "max": 8192, "tooltip": "Height of the mask in pixels."}),
                "shape": (list(SHAPES), {"default": "rectangle", "tooltip": "What to draw. Gradients fade from 0 to 1 instead of drawing a solid shape."}),
                "centre_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Horizontal middle of the shape. 0 is the left edge, 1 the right."}),
                "centre_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Vertical middle of the shape. 0 is the top edge, 1 the bottom."}),
                "size_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Width of the shape as a share of the picture width. For a linear gradient: length of the fade."}),
                "size_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Height of the shape as a share of the picture height. A linear gradient ignores it."}),
                "feather": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.5, "step": 0.01, "tooltip": "Soft edge width as a share of the shorter side. 0 gives a crisp edge."}),
                "angle": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 1.0, "tooltip": "Turns the shape or the gradient direction, in degrees."}),
                "invert": ("BOOLEAN", {"default": False, "tooltip": "On: swap black and white in the finished mask."}),
            }
        }

    def run(self, width, height, shape, centre_x, centre_y, size_x, size_y, feather, angle, invert):
        return (draw_mask(width, height, shape, centre_x, centre_y, size_x, size_y, feather, angle, invert),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskShapeDraw", SYMaskShapeDraw)
NODE_DISPLAY_NAME_MAPPINGS["SYMaskShapeDraw"] = "Mask Shape Draw SY"
