"""Mask Distance Falloff SY: soft edge that depends on the distance from the mask shape."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

SIDES = ("outside", "inside", "both")
CURVES = ("linear", "smooth", "sharp")


def falloff(t, curve):
    """Pure function. Weight 1 at t=0 down to 0 at t=1. Works on numbers and on tensors."""
    if curve not in CURVES:
        raise ValueError("curve must be one of %s, got %r" % (", ".join(CURVES), curve))
    if isinstance(t, (int, float)):
        t = min(1.0, max(0.0, float(t)))
    else:
        t = t.clamp(0.0, 1.0)
    if curve == "linear":
        return 1.0 - t
    if curve == "smooth":
        return 1.0 - t * t * (3.0 - 2.0 * t)
    return (1.0 - t) * (1.0 - t)


def check_args(distance, side, curve):
    """Pure function. Raises ValueError with a plain message for bad settings."""
    if int(distance) < 1 or int(distance) > 256:
        raise ValueError("distance must be between 1 and 256 pixels, got %s" % distance)
    if side not in SIDES:
        raise ValueError("side must be one of %s, got %r" % (", ".join(SIDES), side))
    if curve not in CURVES:
        raise ValueError("curve must be one of %s, got %r" % (", ".join(CURVES), curve))


def outside_value(d, span, curve):
    """Pure function. Value of a pixel d pixels outside the shape (d=0 is the shape itself)."""
    return falloff(d / (span + 1.0), curve)


def inside_value(d, span, curve):
    """Pure function. Value of a pixel at depth d inside the shape (d=1 is the edge pixel)."""
    return 1.0 - falloff((d - 1.0) / span, curve)


def _dilate(x, cross):
    import torch
    import torch.nn.functional as F
    a = F.max_pool2d(x, (3, 1), 1, (1, 0))
    b = F.max_pool2d(x, (1, 3), 1, (0, 1))
    if cross:
        return torch.maximum(a, b)
    return F.max_pool2d(a, (1, 3), 1, (0, 1))


def _distance_from(seed, span):
    """Steps to the nearest seed pixel, capped: 0 = seed, span+1 = further than span."""
    import torch
    cur = seed
    dist = torch.full_like(seed, float(span + 1))
    dist = torch.where(seed > 0.5, torch.zeros_like(dist), dist)
    for k in range(1, span + 1):
        nxt = _dilate(cur, k % 2 == 1)
        new = (nxt > 0.5) & (cur < 0.5)
        if not bool(new.any()):
            break
        dist = torch.where(new, torch.full_like(dist, float(k)), dist)
        cur = nxt
    return dist


def distance_falloff(mask, distance, side, curve):
    """Torch function. mask [B,H,W] float 0..1 -> new mask [B,H,W]."""
    import torch
    check_args(distance, side, curve)
    span = int(distance)
    m = (mask.float() > 0.5).float().unsqueeze(1)
    if side == "outside":
        d = _distance_from(m, span)
        out = falloff(d / (span + 1.0), curve)
    elif side == "inside":
        d = _distance_from(1.0 - m, span)
        out = torch.where(m > 0.5, 1.0 - falloff(((d - 1.0) / span), curve), torch.zeros_like(d))
    else:
        h = max(1, span // 2)
        d_out = _distance_from(m, h)
        d_in = _distance_from(1.0 - m, h)
        out_part = 0.5 * falloff(d_out / (h + 1.0), curve)
        in_part = 1.0 - 0.5 * falloff((d_in - 1.0) / h, curve)
        out = torch.where(m > 0.5, in_part, out_part)
    return out.squeeze(1).clamp(0.0, 1.0)


class SYMaskDistanceFalloff:
    DESCRIPTION = ("Makes a soft edge that depends on how far each pixel is from the mask shape. "
                   "Distance is counted up to the distance setting, so far pixels stay 0 outside and 1 inside.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", {"tooltip": "The mask whose shape the soft edge follows. Pixels above 0.5 count as the shape."}),
                "distance": ("INT", {"default": 24, "min": 1, "max": 256, "tooltip": "How many pixels wide the soft edge is. Longer distances are slower."}),
                "side": (list(SIDES), {"default": "outside", "tooltip": "Outside: shape stays solid, edge fades away from it. Inside: fades inward. Both: centred on the edge."}),
                "curve": (list(CURVES), {"default": "smooth", "tooltip": "Shape of the fade. Smooth is soft at both ends, sharp drops fast near the shape."}),
            }
        }

    def run(self, mask, distance, side, curve):
        if mask.dim() == 2:
            mask = mask.unsqueeze(0)
        return (distance_falloff(mask, distance, side, curve),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskDistanceFalloff", SYMaskDistanceFalloff)
NODE_DISPLAY_NAME_MAPPINGS["SYMaskDistanceFalloff"] = "Mask Distance Falloff SY"
