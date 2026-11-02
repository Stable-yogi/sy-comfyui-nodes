"""Split Toning SY: tint the dark parts one colour and the bright parts another (classic film look)."""
try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae


def hue_to_rgb(hue_degrees):
    """Pure function. Fully saturated, full-brightness colour (r, g, b) for a hue angle in degrees (wraps around 360)."""
    if hue_degrees != hue_degrees:
        raise ValueError("hue must be a number between 0 and 360")
    h = (float(hue_degrees) % 360.0) / 60.0
    out = []
    for n in (5.0, 3.0, 1.0):
        k = (n + h) % 6.0
        f = min(1.0, max(0.0, min(k, 4.0 - k)))
        out.append(1.0 - f)
    return tuple(out)


def split_weights(luma, balance):
    """Pure function. (shadow_w, highlight_w), smooth, add up to 1. balance -1..1 moves the split point:
    below 0 towards the shadows, above 0 towards the highlights."""
    ae.check_range("luma", luma, 0.0, 1.0)
    ae.check_range("balance", balance, -1.0, 1.0)
    mid = 0.5 + 0.3 * balance  # a higher balance moves the split point up, so more of the picture counts as shadow
    t = ae.smoothstep(mid - 0.3, mid + 0.3, luma)
    return 1.0 - t, t


def split_toning_tensor(image, shadow_hue, shadow_sat, highlight_hue, highlight_sat, balance, strength):
    import torch

    ae.check_range("shadow_hue", shadow_hue, 0.0, 360.0)
    ae.check_range("highlight_hue", highlight_hue, 0.0, 360.0)
    ae.check_range("shadow_saturation", shadow_sat, 0.0, 1.0)
    ae.check_range("highlight_saturation", highlight_sat, 0.0, 1.0)
    ae.check_range("balance", balance, -1.0, 1.0)
    ae.check_range("strength", strength, 0.0, 1.0)
    x, was3 = ae.prep_image(image)
    if strength == 0:
        return image.clone()
    rgb = x[..., :3]
    luma = ae.luma_of(rgb).clamp(0.0, 1.0)
    mid = 0.5 + 0.3 * float(balance)
    u = ((luma - (mid - 0.3)) / 0.6).clamp(0.0, 1.0)
    t = u * u * (3.0 - 2.0 * u)

    def tint(hue, sat):
        c = torch.tensor(hue_to_rgb(hue), dtype=rgb.dtype, device=rgb.device)
        cl = c[0] * 0.2126 + c[1] * 0.7152 + c[2] * 0.0722
        return (c - cl) * float(sat)  # zero brightness change: only the colour moves

    off = tint(shadow_hue, shadow_sat) * (1.0 - t) + tint(highlight_hue, highlight_sat) * t
    out = x.clone()
    out[..., :3] = rgb + off * float(strength)
    return ae.finish_image(out, image, was3)


class SYSplitToning:
    DESCRIPTION = ("Tints the dark parts of the picture one colour and the bright parts another, the classic film look. "
                   "The picture keeps its own brightness, only the colour shifts. Strength 0 does nothing.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to tint."}),
            "shadow_hue": ("FLOAT", {"default": 210.0, "min": 0.0, "max": 360.0, "step": 1.0, "tooltip": "Colour of the dark parts as a colour-wheel angle. 210 is blue."}),
            "shadow_saturation": ("FLOAT", {"default": 0.25, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How strong the dark-part tint is. 0 means no tint."}),
            "highlight_hue": ("FLOAT", {"default": 40.0, "min": 0.0, "max": 360.0, "step": 1.0, "tooltip": "Colour of the bright parts as a colour-wheel angle. 40 is warm orange."}),
            "highlight_saturation": ("FLOAT", {"default": 0.25, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How strong the bright-part tint is. 0 means no tint."}),
            "balance": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Moves the split: below 0 towards the shadows, above 0 towards the highlights."}),
            "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Overall mix of the effect. 0 returns the original picture."}),
        }}

    def run(self, image, shadow_hue, shadow_saturation, highlight_hue, highlight_saturation, balance, strength):
        return (split_toning_tensor(image, float(shadow_hue), float(shadow_saturation), float(highlight_hue),
                                    float(highlight_saturation), float(balance), float(strength)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SplitToning", SYSplitToning)
NODE_DISPLAY_NAME_MAPPINGS["SYSplitToning"] = "Split Toning SY"
