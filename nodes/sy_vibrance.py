"""Vibrance SY: lifts dull colours more than strong ones, and goes easy on skin tones."""
try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae

SKIN_LOW, SKIN_HIGH = 5.0, 50.0   # hue range (degrees) that counts as skin
SKIN_HOLD = 0.5                   # how much of a lift skin tones give up at most


def skin_weight(hue):
    """Pure function. 1 inside the skin hue range, fading to 0 outside it. Hue in degrees."""
    hue = float(hue) % 360.0
    if SKIN_LOW <= hue <= SKIN_HIGH:
        return 1.0
    d = min(abs(hue - SKIN_LOW), abs(hue - SKIN_HIGH))
    return 1.0 - ae.smoothstep(0.0, 15.0, d)


def vibrance_gain(sat, amount, skin=0.0):
    """Pure function. Colour strength factor for a pixel with saturation `sat` (0..1).
    Low saturation gets the most lift, high almost none. `skin` (0..1) holds back part of a lift."""
    ae.check_range("sat", sat, 0.0, 1.0)
    ae.check_range("amount", amount, -1.0, 1.0)
    ae.check_range("skin", skin, 0.0, 1.0)
    eff = amount * (1.0 - SKIN_HOLD * skin) if amount > 0 else amount
    return 1.0 + eff * (1.0 - sat)


def vibrance_tensor(image, amount):
    import torch

    ae.check_range("amount", amount, -1.0, 1.0)
    x, was3 = ae.prep_image(image)
    if amount == 0:
        return image.clone()
    rgb = x[..., :3]
    h, s, _v = ae.rgb_to_hsv(rgb)
    # same maths as vibrance_gain and skin_weight, on whole tensors
    d = torch.minimum((h - SKIN_LOW).abs(), (h - SKIN_HIGH).abs())
    inside = (h >= SKIN_LOW) & (h <= SKIN_HIGH)
    t = (d / 15.0).clamp(0.0, 1.0)
    skin = torch.where(inside, torch.ones_like(t), 1.0 - t * t * (3.0 - 2.0 * t))
    eff = amount * (1.0 - SKIN_HOLD * skin) if amount > 0 else torch.full_like(skin, float(amount))
    gain = 1.0 + eff * (1.0 - s)
    grey = ae.luma_of(rgb)
    out = x.clone()
    out[..., :3] = grey + (rgb - grey) * gain
    return ae.finish_image(out, image, was3)


class SYVibrance:
    DESCRIPTION = ("Makes dull colours richer without blowing out the colours that are already strong. "
                   "Skin tones are protected a little. Negative values calm the weak colours instead.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to give richer colours."}),
            "amount": ("FLOAT", {"default": 0.4, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Above 0 lifts dull colours. Below 0 mutes them. 0 does nothing."}),
        }}

    def run(self, image, amount):
        return (vibrance_tensor(image, float(amount)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Vibrance", SYVibrance)
NODE_DISPLAY_NAME_MAPPINGS["SYVibrance"] = "Vibrance SY"
