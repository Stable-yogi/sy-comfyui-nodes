"""Selective Colour SY: changes only one range of colours, for example just the greens."""
try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae


def hue_distance(a, b):
    """Pure function. Shortest distance in degrees between two hues on the 360 circle."""
    d = abs(float(a) - float(b)) % 360.0
    return min(d, 360.0 - d)


def hue_weight(hue, centre, width, softness):
    """Pure function. 0..1: how much a pixel of this hue is inside the chosen range.
    The range spans `width` degrees around `centre`; `softness` (0..1) makes the edge fade."""
    ae.check_range("hue_width", width, 0.0, 360.0)
    ae.check_range("softness", softness, 0.0, 1.0)
    d = hue_distance(hue, centre)
    outer = width / 2.0
    inner = outer * (1.0 - softness)
    if d <= inner:
        return 1.0
    if d >= outer:
        return 0.0
    return 1.0 - ae.smoothstep(inner, outer, d)


def selective_tensor(image, hue_centre, hue_width, softness, hue_shift, saturation, brightness):
    import torch

    ae.check_range("hue_centre", hue_centre, 0.0, 360.0)
    ae.check_range("hue_width", hue_width, 5.0, 180.0)
    ae.check_range("softness", softness, 0.0, 1.0)
    ae.check_range("hue_shift", hue_shift, -180.0, 180.0)
    ae.check_range("saturation", saturation, -1.0, 1.0)
    ae.check_range("brightness", brightness, -1.0, 1.0)
    x, was3 = ae.prep_image(image)
    if hue_shift == 0 and saturation == 0 and brightness == 0:
        return image.clone()
    rgb = x[..., :3]
    h, s, v = ae.rgb_to_hsv(rgb)
    d = (h - hue_centre).abs() % 360.0
    d = torch.minimum(d, 360.0 - d)
    outer = hue_width / 2.0
    inner = outer * (1.0 - softness)
    t = ((d - inner) / max(outer - inner, 1e-6)).clamp(0.0, 1.0)
    w = torch.where(d <= inner, torch.ones_like(t),
                    torch.where(d >= outer, torch.zeros_like(t), 1.0 - t * t * (3.0 - 2.0 * t)))
    w = w * (s * 4.0).clamp(0.0, 1.0)   # grey pixels have no real hue: leave them alone
    h2 = torch.remainder(h + hue_shift * w, 360.0)
    s2 = (s * (1.0 + saturation * w)).clamp(0.0, 1.0)
    v2 = (v * (1.0 + brightness * w)).clamp(0.0, 1.0)
    out = x.clone()
    out[..., :3] = ae.hsv_to_rgb(h2, s2, v2)
    return ae.finish_image(out, image, was3)


class SYSelectiveColour:
    DESCRIPTION = ("Changes only one range of colours, for example just the greens or just the blues. "
                   "Pick the colour with hue_centre, then shift it, make it stronger or weaker, or brighter or darker.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to change."}),
            "hue_centre": ("FLOAT", {"default": 120.0, "min": 0.0, "max": 360.0, "step": 1.0, "tooltip": "The colour to change, as degrees on the colour wheel. 0 red, 120 green, 240 blue."}),
            "hue_width": ("FLOAT", {"default": 40.0, "min": 5.0, "max": 180.0, "step": 1.0, "tooltip": "How wide a range of colours around the centre is changed, in degrees."}),
            "softness": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "0 gives a hard edge to the range. 1 fades it out smoothly."}),
            "hue_shift": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0, "tooltip": "Turns the chosen colours round the colour wheel, in degrees."}),
            "saturation": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Makes the chosen colours stronger (above 0) or weaker (below 0)."}),
            "brightness": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Makes the chosen colours brighter (above 0) or darker (below 0)."}),
        }}

    def run(self, image, hue_centre, hue_width, softness, hue_shift, saturation, brightness):
        return (selective_tensor(image, float(hue_centre), float(hue_width), float(softness),
                                 float(hue_shift), float(saturation), float(brightness)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SelectiveColour", SYSelectiveColour)
NODE_DISPLAY_NAME_MAPPINGS["SYSelectiveColour"] = "Selective Colour SY"
