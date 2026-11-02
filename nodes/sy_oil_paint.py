"""Oil Paint SY: painterly smoothing that keeps edges (four-window Kuwahara)."""
try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae


def pick_lowest(variances):
    """Pure function. Index of the smallest value (the first one when there is a tie)."""
    vals = list(variances)
    if not vals:
        raise ValueError("nothing to choose from: give at least one variance")
    best = 0
    for i, v in enumerate(vals):
        if v < vals[best]:
            best = i
    return best


def oil_tensor(image, radius):
    import torch
    import torch.nn.functional as F

    ae.check_range("radius", radius, 1, 10)
    r = int(radius)
    x, was3 = ae.prep_image(image)
    rgb = x[..., :3].permute(0, 3, 1, 2)
    b, _c, h, w = rgb.shape
    luma = ae.luma_of(x[..., :3]).permute(0, 3, 1, 2)
    k = r + 1

    def box(t):
        # mean of every k x k window; window at [i, j] covers padded rows i..i+r, columns j..j+r
        return F.avg_pool2d(F.pad(t, (r, r, r, r), mode="replicate"), k, stride=1)

    mean_rgb = box(rgb)
    mean_l = box(luma)
    var = (box(luma * luma) - mean_l * mean_l).clamp(min=0.0)
    # four windows that all contain the pixel: top-left, top-right, bottom-left, bottom-right
    offs = ((0, 0), (0, r), (r, 0), (r, r))
    means = torch.stack([mean_rgb[..., oy:oy + h, ox:ox + w] for oy, ox in offs], dim=0)   # [4,B,3,H,W]
    vars_ = torch.stack([var[..., oy:oy + h, ox:ox + w] for oy, ox in offs], dim=0)        # [4,B,1,H,W]
    pick = vars_.argmin(dim=0, keepdim=True)                                             # [1,B,1,H,W]
    chosen = torch.gather(means, 0, pick.expand(1, b, 3, h, w))[0]
    out = x.clone()
    out[..., :3] = chosen.permute(0, 2, 3, 1)
    return ae.finish_image(out, image, was3)


class SYOilPaint:
    DESCRIPTION = ("Gives the picture a painted look. Each pixel takes the average colour of the calmest "
                   "of four neighbouring patches, so areas turn smooth while edges stay sharp.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to turn into a painting."}),
            "radius": ("INT", {"default": 4, "min": 1, "max": 10, "tooltip": "Size of the brush patches in pixels. Bigger gives broader strokes and runs slower."}),
        }}

    def run(self, image, radius):
        return (oil_tensor(image, int(radius)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "OilPaint", SYOilPaint)
NODE_DISPLAY_NAME_MAPPINGS["SYOilPaint"] = "Oil Paint SY"
