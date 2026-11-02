"""Lens Distortion SY: barrel (bulge) or pincushion (pinch) warp."""
try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae

EDGES = ("stretch", "black", "mirror")
STRENGTH = 0.3  # keeps the warp smooth (never folds back on itself) at amount 1
_PAD_MODE = {"stretch": "border", "black": "zeros", "mirror": "reflection"}


def radial_scale(r, amount):
    """Pure function. Where to read the source for an output pixel at distance r (0 = centre, 1 = corner).
    amount > 0 reads closer to the centre (barrel: the middle bulges), amount < 0 reads further out (pincushion)."""
    ae.check_range("amount", amount, -1.0, 1.0)
    return r * (1.0 - STRENGTH * amount * r * r)


def lens_tensor(image, amount, edge):
    import torch
    import torch.nn.functional as F

    ae.check_range("amount", amount, -1.0, 1.0)
    if edge not in EDGES:
        raise ValueError("edge must be one of %s, got %r" % (", ".join(EDGES), edge))
    x, was3 = ae.prep_image(image, need_colour=False)
    if amount == 0:
        return image.clone()
    b, h, w, c = x.shape
    ys = (torch.arange(h, dtype=torch.float32, device=x.device) + 0.5) / h * 2.0 - 1.0
    xs = (torch.arange(w, dtype=torch.float32, device=x.device) + 0.5) / w * 2.0 - 1.0
    gy, gx = torch.meshgrid(ys, xs, indexing="ij")
    half_diag = (w * w + h * h) ** 0.5 / 2.0
    r = ((gx * w / 2.0) ** 2 + (gy * h / 2.0) ** 2).sqrt() / half_diag
    ratio = 1.0 - STRENGTH * amount * r * r          # radial_scale(r, amount) / r
    grid = torch.stack((gx * ratio, gy * ratio), dim=-1).unsqueeze(0).expand(b, -1, -1, -1)
    out = F.grid_sample(x.permute(0, 3, 1, 2), grid, mode="bilinear",
                        padding_mode=_PAD_MODE[edge], align_corners=False)
    return ae.finish_image(out.permute(0, 2, 3, 1), image, was3)


class SYLensDistortion:
    DESCRIPTION = ("Bends the picture like a camera lens. Positive amounts bulge the middle outwards (barrel), "
                   "negative amounts pinch it inwards (pincushion). 0 leaves the picture exactly as it is.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to bend."}),
            "amount": ("FLOAT", {"default": 0.2, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Above 0 bulges the middle (barrel). Below 0 pinches it (pincushion). 0 does nothing."}),
            "edge": (list(EDGES), {"default": "stretch", "tooltip": "What fills the border when the bend pulls in space: stretch the edge, black, or mirror the picture."}),
        }}

    def run(self, image, amount, edge):
        return (lens_tensor(image, float(amount), edge),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LensDistortion", SYLensDistortion)
NODE_DISPLAY_NAME_MAPPINGS["SYLensDistortion"] = "Lens Distortion SY"
