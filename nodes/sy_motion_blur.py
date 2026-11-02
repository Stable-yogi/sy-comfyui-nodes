"""Motion Blur SY: smear a picture along a direction, like a moving camera."""
import math

try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae

SHAPES = ["even", "fade out", "centred"]


def blur_taps(length, angle_degrees, samples, shape):
    """Pure function. List of (dx, dy, weight): where to look (pixels, y grows downwards) and how much it counts.
    Angle 0 smears to the right, 90 smears upwards. Weights add up to 1."""
    ae.check_range("length", length, 1, 400)
    ae.check_range("angle", angle_degrees, 0.0, 360.0)
    ae.check_range("samples", samples, 3, 64)
    if shape not in SHAPES:
        raise ValueError("shape must be one of %s, got %r" % (", ".join(SHAPES), shape))
    samples = int(samples)
    if length <= 1:
        return [(0.0, 0.0, 1.0)]
    a = math.radians(angle_degrees)
    ux, uy = math.cos(a), -math.sin(a)
    taps = []
    for i in range(samples):
        t = i / float(samples - 1)
        pos = t - 0.5 if shape == "centred" else t
        wgt = 1.0 - i / float(samples) if shape == "fade out" else 1.0
        taps.append((pos * length * ux, pos * length * uy, wgt))
    total = sum(t[2] for t in taps)
    return [(dx, dy, w / total) for dx, dy, w in taps]


def blur_tensor(image, length, angle, shape, samples):
    ae.check_range("length", length, 1, 400)
    ae.check_range("angle", angle, 0.0, 360.0)
    ae.check_range("samples", samples, 3, 64)
    if shape not in SHAPES:
        raise ValueError("shape must be one of %s, got %r" % (", ".join(SHAPES), shape))
    import torch
    import torch.nn.functional as F

    x, was3 = ae.prep_image(image, need_colour=False)
    if length <= 1:
        return image.clone()
    taps = blur_taps(length, angle, samples, shape)
    b, h, w, c = x.shape
    src = x.permute(0, 3, 1, 2).contiguous()
    ys = (torch.arange(h, device=x.device, dtype=torch.float32) + 0.5) / h * 2.0 - 1.0
    xs = (torch.arange(w, device=x.device, dtype=torch.float32) + 0.5) / w * 2.0 - 1.0
    base = torch.stack((xs.view(1, w).expand(h, w), ys.view(h, 1).expand(h, w)), dim=-1).unsqueeze(0)
    acc = torch.zeros_like(src)
    for dx, dy, wt in taps:
        # a pixel gets what lies dx, dy behind it, so the smear trails in the angle direction
        shift = torch.tensor([-dx * 2.0 / w, -dy * 2.0 / h], device=x.device, dtype=torch.float32)
        grid = (base + shift).expand(b, h, w, 2)
        acc += F.grid_sample(src, grid, mode="bilinear", padding_mode="border", align_corners=False) * wt
    return ae.finish_image(acc.permute(0, 2, 3, 1), image, was3)


class SYMotionBlur:
    DESCRIPTION = ("Smears the picture along a direction, like a camera or object that moved while the photo was taken. "
                   "Angle 0 smears to the right. Length 1 does nothing.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to smear."}),
            "length": ("INT", {"default": 30, "min": 1, "max": 400, "tooltip": "How far the smear reaches, in pixels. 1 does nothing."}),
            "angle": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 1.0, "tooltip": "Direction of the smear in degrees. 0 is to the right, 90 is up."}),
            "shape": (SHAPES, {"default": "even", "tooltip": "even: same strength all along. fade out: trail that fades. centred: both sides."}),
            "samples": ("INT", {"default": 16, "min": 3, "max": 64, "tooltip": "How many copies are mixed. More is smoother but slower."}),
        }}

    def run(self, image, length, angle, shape, samples):
        return (blur_tensor(image, int(length), float(angle), shape, int(samples)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MotionBlur", SYMotionBlur)
NODE_DISPLAY_NAME_MAPPINGS["SYMotionBlur"] = "Motion Blur SY"
