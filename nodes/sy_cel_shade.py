"""Cel Shade SY: cartoon look with flat colour steps and ink outlines."""
try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae

EDGE_LOW, EDGE_HIGH = 0.04, 0.25  # edge strength (0..1) that starts / fully draws the ink line


def quantise_levels(value, levels):
    """Pure function. Snaps a brightness 0..1 to the nearest of `levels` flat steps (first step 0, last step 1)."""
    levels = int(levels)
    if levels < 2:
        raise ValueError("levels must be at least 2, got %d" % levels)
    value = min(1.0, max(0.0, float(value)))
    return round(value * (levels - 1)) / (levels - 1)


def edge_amount(magnitude):
    """Pure function. 0..1 ink strength for an edge magnitude (0..1)."""
    return ae.smoothstep(EDGE_LOW, EDGE_HIGH, magnitude)


def cel_tensor(image, levels, smooth, outline, outline_width):
    import torch
    import torch.nn.functional as F

    ae.check_range("levels", levels, 2, 12)
    ae.check_range("smooth", smooth, 0.0, 3.0)
    ae.check_range("outline", outline, 0.0, 1.0)
    ae.check_range("outline_width", outline_width, 1, 6)
    x, was3 = ae.prep_image(image)
    rgb = x[..., :3]
    work = rgb
    if smooth > 0:
        work = ae.blur_nchw(rgb.permute(0, 3, 1, 2), float(smooth)).permute(0, 2, 3, 1)
    luma = ae.luma_of(work)
    q = torch.round(luma.clamp(0.0, 1.0) * (levels - 1)) / (levels - 1)
    scale = q / luma.clamp(min=1e-4)
    flat = work * scale
    # pixels with no brightness take the flat grey of their step
    flat = torch.where(luma > 1e-4, flat, q.expand_as(flat))
    # a colour pushed past white is pulled back toward grey, so the step brightness stays exact
    over = flat.amax(dim=-1, keepdim=True) - q
    keep = torch.where(over > 1e-6, ((1.0 - q) / over.clamp(min=1e-6)).clamp(max=1.0), torch.ones_like(q))
    flat = q + (flat - q) * keep
    if outline > 0:
        lum = ae.luma_of(work).permute(0, 3, 1, 2)
        p = F.pad(lum, (1, 1, 1, 1), mode="replicate")
        a, b_, c = p[..., :-2, :-2], p[..., :-2, 1:-1], p[..., :-2, 2:]
        d, f = p[..., 1:-1, :-2], p[..., 1:-1, 2:]
        g, h, i = p[..., 2:, :-2], p[..., 2:, 1:-1], p[..., 2:, 2:]
        gx = (c + 2 * f + i) - (a + 2 * d + g)
        gy = (g + 2 * h + i) - (a + 2 * b_ + c)
        mag = ((gx * gx + gy * gy).sqrt() / 4.0).clamp(0.0, 1.0)
        t = ((mag - EDGE_LOW) / (EDGE_HIGH - EDGE_LOW)).clamp(0.0, 1.0)
        edge = t * t * (3.0 - 2.0 * t)
        if outline_width > 1:
            k = 2 * int(outline_width) - 1
            edge = F.max_pool2d(edge, k, stride=1, padding=k // 2)
        flat = flat * (1.0 - float(outline) * edge.permute(0, 2, 3, 1))
    out = x.clone()
    out[..., :3] = flat
    return ae.finish_image(out, image, was3)


class SYCelShade:
    DESCRIPTION = ("Gives the picture a cartoon look: smooth colours are cut into a few flat steps of brightness "
                   "and dark ink lines are drawn along the edges.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to turn into a cartoon."}),
            "levels": ("INT", {"default": 5, "min": 2, "max": 12, "tooltip": "How many flat brightness steps to use. Fewer looks more graphic."}),
            "smooth": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.1, "tooltip": "Softens small detail first so the steps and lines come out clean. 0 skips it."}),
            "outline": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How dark the ink lines are. 0 draws no lines."}),
            "outline_width": ("INT", {"default": 1, "min": 1, "max": 6, "tooltip": "How thick the ink lines are, in pixels."}),
        }}

    def run(self, image, levels, smooth, outline, outline_width):
        return (cel_tensor(image, int(levels), float(smooth), float(outline), int(outline_width)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CelShade", SYCelShade)
NODE_DISPLAY_NAME_MAPPINGS["SYCelShade"] = "Cel Shade SY"
