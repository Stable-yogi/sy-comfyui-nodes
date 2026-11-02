"""Colour Balance 3-Way SY: tints shadows, mid-tones and highlights separately."""
try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae

MAX_SHIFT = 0.25  # a slider at 1 moves a colour channel by this much


def zone_weights(luma):
    """Pure function. (shadow, mid, high) weights for a brightness 0..1. They always add up to 1."""
    ae.check_range("luma", luma, 0.0, 1.0)
    if luma <= 0.5:
        mid = ae.smoothstep(0.0, 0.5, luma)
        return (1.0 - mid, mid, 0.0)
    high = ae.smoothstep(0.5, 1.0, luma)
    return (0.0, 1.0 - high, high)


def balance_tensor(image, shadow, mid, high, strength):
    """Torch. shadow/mid/high are (r,g,b) sliders in -1..1."""
    import torch

    for name, trio in (("shadow", shadow), ("mid", mid), ("high", high)):
        for v in trio:
            ae.check_range(name + " slider", v, -1.0, 1.0)
    ae.check_range("strength", strength, 0.0, 1.0)
    x, was3 = ae.prep_image(image)
    if strength == 0 or not any(v for trio in (shadow, mid, high) for v in trio):
        return image.clone()
    rgb = x[..., :3]
    luma = ae.luma_of(rgb).clamp(0.0, 1.0)
    lo = luma <= 0.5
    t_lo = (luma / 0.5).clamp(0.0, 1.0)
    t_hi = ((luma - 0.5) / 0.5).clamp(0.0, 1.0)
    mid_lo = t_lo * t_lo * (3.0 - 2.0 * t_lo)
    high_w = torch.where(lo, torch.zeros_like(luma), t_hi * t_hi * (3.0 - 2.0 * t_hi))
    shadow_w = torch.where(lo, 1.0 - mid_lo, torch.zeros_like(luma))
    mid_w = 1.0 - shadow_w - high_w
    dev = x.device
    s = torch.tensor(shadow, dtype=x.dtype, device=dev)
    m = torch.tensor(mid, dtype=x.dtype, device=dev)
    h = torch.tensor(high, dtype=x.dtype, device=dev)
    shift = (shadow_w * s + mid_w * m + high_w * h) * (MAX_SHIFT * float(strength))
    out = x.clone()
    out[..., :3] = rgb + shift
    return ae.finish_image(out, image, was3)


def _slider(tip):
    return ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": tip})


class SYColourBalance3Way:
    DESCRIPTION = ("Tints the dark parts, the middle and the bright parts of a picture separately. "
                   "Push red, green or blue up or down in each zone. All sliders at 0 do nothing.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        req = {"image": ("IMAGE", {"tooltip": "The picture or pictures to tint."})}
        for zone, label in (("shadow", "dark parts"), ("mid", "middle tones"), ("high", "bright parts")):
            for ch, word in (("red", "red (up) or cyan (down)"), ("green", "green (up) or magenta (down)"),
                             ("blue", "blue (up) or yellow (down)")):
                req["%s_%s" % (zone, ch)] = _slider("Tint of the %s: %s." % (label, word))
        req["strength"] = ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How much of the tint is used. 0 gives the original picture."})
        return {"required": req}

    def run(self, image, shadow_red, shadow_green, shadow_blue, mid_red, mid_green, mid_blue,
            high_red, high_green, high_blue, strength):
        return (balance_tensor(image, (float(shadow_red), float(shadow_green), float(shadow_blue)),
                               (float(mid_red), float(mid_green), float(mid_blue)),
                               (float(high_red), float(high_green), float(high_blue)), float(strength)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ColourBalance3Way", SYColourBalance3Way)
NODE_DISPLAY_NAME_MAPPINGS["SYColourBalance3Way"] = "Colour Balance 3-Way SY"
