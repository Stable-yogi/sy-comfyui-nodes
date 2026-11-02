"""Defocus Blur SY: round camera-lens blur where bright points become soft discs."""
import math

try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae

SHAPES = ["disc", "hexagon"]
EDGES = ["replicate", "mirror"]
MAX_TAPS = 400
BIG_RADIUS = 7.0  # above this the blur runs on a shrunken copy so big pictures stay fast
_SQ3 = math.sqrt(3.0)


def _inside(x, y, radius, shape):
    if shape == "disc":
        return x * x + y * y <= radius * radius + 1e-9
    return abs(y) <= radius * _SQ3 / 2.0 + 1e-9 and _SQ3 * abs(x) + abs(y) <= _SQ3 * radius + 1e-9


def disc_offsets(radius, shape="disc", max_taps=MAX_TAPS):
    """Pure function. Whole-pixel (dx, dy) offsets inside the shape; each one counts the same.
    Up to max_taps every pixel is used. Bigger shapes use a regular grid with a wider step so the count stays at or under max_taps."""
    ae.check_range("radius", radius, 0.0, 200.0)
    if shape not in SHAPES:
        raise ValueError("shape must be one of %s, got %r" % (SHAPES, shape))
    if int(max_taps) < 1:
        raise ValueError("max_taps must be at least 1, got %s" % max_taps)
    max_taps = int(max_taps)
    r = int(math.floor(radius))
    pts = [(dx, dy) for dy in range(-r, r + 1) for dx in range(-r, r + 1) if _inside(dx, dy, radius, shape)]
    if len(pts) <= max_taps:
        return pts or [(0, 0)]
    step = math.sqrt(len(pts) / float(max_taps))
    while True:
        out = []
        k = int(math.floor(radius / step))
        for j in range(-k, k + 1):
            for i in range(-k, k + 1):
                x, y = i * step, j * step
                if _inside(x, y, radius, shape):
                    out.append((int(round(x)), int(round(y))))
        if len(out) <= max_taps:
            return out or [(0, 0)]
        step *= 1.02


def highlight_gain(luma, boost):
    """Pure function. Weight a pixel gets in the blur: 1 for dark pixels, up to 1 + 15 * boost for white ones (rises like luma^4).
    The blur is a weighted average, so bright pixels are raised before the blur and lowered back after it."""
    ae.check_range("luma", luma, 0.0, 1.0)
    ae.check_range("boost", boost, 0.0, 1.0)
    return 1.0 + 15.0 * boost * luma ** 4


def defocus_tensor(image, radius, shape, highlight_boost, edge):
    import torch
    import torch.nn.functional as F

    ae.check_range("radius", radius, 0.0, 60.0)
    ae.check_range("highlight_boost", highlight_boost, 0.0, 1.0)
    if shape not in SHAPES:
        raise ValueError("shape must be one of %s, got %r" % (SHAPES, shape))
    if edge not in EDGES:
        raise ValueError("edge must be one of %s, got %r" % (EDGES, edge))
    x, was3 = ae.prep_image(image)
    if radius < 0.5:
        return image.clone()
    rgb = x[..., :3].permute(0, 3, 1, 2)
    h, w = rgb.shape[2], rgb.shape[3]
    eff = float(radius)
    sh, sw = h, w
    rgb_s = rgb
    if eff > BIG_RADIUS:
        f = eff / BIG_RADIUS
        th, tw = max(1, int(round(h / f))), max(1, int(round(w / f)))
        eff = BIG_RADIUS
        if th < h or tw < w:
            sh, sw = th, tw
            rgb_s = F.interpolate(rgb, size=(sh, sw), mode="area")
    offs = disc_offsets(eff, shape, MAX_TAPS)
    pad = max(1, max(max(abs(dx), abs(dy)) for dx, dy in offs))
    luma = ae.luma_of(rgb_s.permute(0, 2, 3, 1)).permute(0, 3, 1, 2).clamp(0.0, 1.0)
    wgt = 1.0 + 15.0 * float(highlight_boost) * luma ** 4
    src = torch.cat([rgb_s * wgt, wgt], dim=1)
    mode = "reflect" if edge == "mirror" and pad < min(sh, sw) else "replicate"
    xp = F.pad(src, (pad, pad, pad, pad), mode=mode)
    acc = torch.zeros_like(src)
    for dx, dy in offs:
        acc += xp[:, :, pad + dy:pad + dy + sh, pad + dx:pad + dx + sw]
    del xp
    res = acc[:, :3] / acc[:, 3:4].clamp_min(1e-6)
    if (sh, sw) != (h, w):
        res = F.interpolate(res, size=(h, w), mode="bilinear", align_corners=False)
    out = x.clone()
    out[..., :3] = res.permute(0, 2, 3, 1)
    return ae.finish_image(out, image, was3)


class SYDefocusBlur:
    DESCRIPTION = ("Blurs like a camera lens that is out of focus: bright points turn into soft round discs. "
                   "Highlight boost lets bright points glow into clear discs. Radius under 0.5 does nothing.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to blur."}),
            "radius": ("FLOAT", {"default": 8.0, "min": 0.5, "max": 60.0, "step": 0.5, "tooltip": "Size of the blur discs in pixels. Bigger is blurrier."}),
            "shape": (SHAPES, {"default": "disc", "tooltip": "Shape of the lens opening: round disc or six-sided hexagon."}),
            "highlight_boost": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Makes bright points glow into clear discs. 0 is a plain even blur."}),
            "edge": (EDGES, {"default": "replicate", "tooltip": "What fills the area beyond the picture edge: copy the edge pixels or mirror the picture."}),
        }}

    def run(self, image, radius, shape, highlight_boost, edge):
        return (defocus_tensor(image, float(radius), shape, float(highlight_boost), edge),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DefocusBlur", SYDefocusBlur)
NODE_DISPLAY_NAME_MAPPINGS["SYDefocusBlur"] = "Defocus Blur SY"
