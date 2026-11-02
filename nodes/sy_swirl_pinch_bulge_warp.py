"""Swirl Pinch Bulge Warp SY: twist, pinch or bulge a picture around a point."""
import math

try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae

MODES = ["swirl", "pinch", "bulge"]
EDGES = ["stretch", "mirror", "black"]


def _falloff(r_norm):
    """Pure function. 1 at the centre, 0 at the radius and beyond, smooth in between."""
    return 1.0 - ae.smoothstep(0.0, 1.0, r_norm)


def warp_scale(r_norm, mode, strength):
    """Pure function. For swirl: the turn angle in radians at normalised distance r_norm.
    For pinch and bulge: the factor the sampling distance is multiplied by.
    At r_norm >= 1 there is no change (angle 0, factor 1), and the change fades smoothly towards it."""
    if mode not in MODES:
        raise ValueError("mode must be one of %s, got %r" % (", ".join(MODES), mode))
    ae.check_range("strength", strength, -2.0, 2.0)
    if r_norm != r_norm or r_norm < 0:
        raise ValueError("r_norm must be 0 or more, got %s" % r_norm)
    if r_norm >= 1.0:
        return 0.0 if mode == "swirl" else 1.0
    w = _falloff(r_norm)
    if mode == "swirl":
        return strength * math.pi * w * w
    if mode == "bulge":
        return max(0.02, 1.0 - 0.45 * strength * w)
    return max(0.02, 1.0 + 0.45 * strength * w)


def warp_tensor(image, mode, strength, radius, centre_x, centre_y, edge):
    if mode not in MODES:
        raise ValueError("mode must be one of %s, got %r" % (", ".join(MODES), mode))
    if edge not in EDGES:
        raise ValueError("edge must be one of %s, got %r" % (", ".join(EDGES), edge))
    ae.check_range("strength", strength, -2.0, 2.0)
    ae.check_range("radius", radius, 0.05, 1.5)
    ae.check_range("centre_x", centre_x, 0.0, 1.0)
    ae.check_range("centre_y", centre_y, 0.0, 1.0)
    import torch
    import torch.nn.functional as F

    x, was3 = ae.prep_image(image, need_colour=False)
    if strength == 0:
        return image.clone()
    b, h, w, c = x.shape
    dev = x.device
    ys = torch.arange(h, device=dev, dtype=torch.float32).view(h, 1).expand(h, w) + 0.5
    xs = torch.arange(w, device=dev, dtype=torch.float32).view(1, w).expand(h, w) + 0.5
    cx, cy = centre_x * w, centre_y * h
    rad = max(1.0, radius * min(h, w))
    dx, dy = xs - cx, ys - cy
    dist = torch.sqrt(dx * dx + dy * dy)
    rn = dist / rad
    inside = rn < 1.0
    wgt = 1.0 - rn.clamp(0, 1) * rn.clamp(0, 1) * (3.0 - 2.0 * rn.clamp(0, 1))
    if mode == "swirl":
        ang = strength * math.pi * wgt * wgt
        co, si = torch.cos(ang), torch.sin(ang)
        sx, sy = dx * co - dy * si, dx * si + dy * co
    else:
        k = 0.45 * strength * wgt
        fac = (1.0 - k) if mode == "bulge" else (1.0 + k)
        fac = fac.clamp(min=0.02)
        sx, sy = dx * fac, dy * fac
    sx = torch.where(inside, sx + cx, xs)
    sy = torch.where(inside, sy + cy, ys)
    grid = torch.stack((sx / w * 2.0 - 1.0, sy / h * 2.0 - 1.0), dim=-1).unsqueeze(0)
    pad = {"stretch": "border", "mirror": "reflection", "black": "zeros"}[edge]
    src = x.permute(0, 3, 1, 2)
    warped = F.grid_sample(src, grid.expand(b, h, w, 2), mode="bilinear", padding_mode=pad, align_corners=False)
    out = torch.where(inside.view(1, 1, h, w), warped, src)
    return ae.finish_image(out.permute(0, 2, 3, 1), image, was3)


class SYSwirlPinchBulgeWarp:
    DESCRIPTION = ("Twists, pinches or bulges the picture around a point. Swirl turns the picture, pinch pulls it towards the point, "
                   "bulge pushes it out like a lens. Pixels outside the radius stay as they are.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to warp."}),
            "mode": (MODES, {"default": "swirl", "tooltip": "swirl twists, pinch pulls inwards, bulge pushes outwards."}),
            "strength": ("FLOAT", {"default": 0.6, "min": -2.0, "max": 2.0, "step": 0.01, "tooltip": "How strong the warp is. Negative goes the other way. 0 does nothing."}),
            "radius": ("FLOAT", {"default": 0.5, "min": 0.05, "max": 1.5, "step": 0.01, "tooltip": "Size of the warped area, as a fraction of the shorter side."}),
            "centre_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Where the warp is centred across the picture. 0 is the left edge, 1 the right edge."}),
            "centre_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Where the warp is centred down the picture. 0 is the top edge, 1 the bottom edge."}),
            "edge": (EDGES, {"default": "stretch", "tooltip": "What fills places that the warp pulls from outside the picture."}),
        }}

    def run(self, image, mode, strength, radius, centre_x, centre_y, edge):
        return (warp_tensor(image, mode, float(strength), float(radius), float(centre_x), float(centre_y), edge),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SwirlPinchBulgeWarp", SYSwirlPinchBulgeWarp)
NODE_DISPLAY_NAME_MAPPINGS["SYSwirlPinchBulgeWarp"] = "Swirl Pinch Bulge Warp SY"
