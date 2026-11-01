"""Brightness Contrast SY: makes a picture lighter or darker and flatter or punchier."""
import math

try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from ._sy_d1_finish import MASK_TIP, MIX_TIP, ENABLED_TIP, finish_rgb, info_line
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    from _sy_d1_finish import MASK_TIP, MIX_TIP, ENABLED_TIP, finish_rgb, info_line


def check_range(name, v):
    if not -100.0 <= v <= 100.0:
        raise ValueError("%s must be between -100 and 100, got %s" % (name, v))


def contrast_factor(contrast):
    """Pure function. 1.0 at 0; below 1 flattens, above 1 adds punch."""
    c = max(-99.0, min(99.0, float(contrast)))
    return math.tan((c / 100.0 + 1.0) * math.pi / 4.0)


def bc_value(v, brightness, contrast):
    """Pure function. One channel value 0..1. 0 and 0 return the value unchanged."""
    check_range("brightness", brightness)
    check_range("contrast", contrast)
    if brightness == 0 and contrast == 0:
        return v
    o = (v - 0.5) * contrast_factor(contrast) + 0.5 + brightness / 100.0
    return 0.0 if o < 0.0 else 1.0 if o > 1.0 else o


class SYBrightnessContrast:
    DESCRIPTION = ("Makes a picture lighter or darker, and flatter or punchier. Adds a mask (change only the white part), a mix slider "
                   "to blend with the original, an on/off switch and an info line, and keeps transparency. Both at 0 leaves the picture as it is.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to change."}),
                "brightness": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "tooltip": "Below 0 darkens, above 0 lightens."}),
                "contrast": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "tooltip": "Below 0 flattens the picture, above 0 pushes lights and darks apart."}),
            },
            "optional": {
                "mask": ("MASK", {"tooltip": MASK_TIP}),
                "mix": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": MIX_TIP}),
                "enabled": ("BOOLEAN", {"default": True, "tooltip": ENABLED_TIP}),
            },
        }

    def run(self, image, brightness, contrast, mask=None, mix=1.0, enabled=True):
        import torch

        need_image(image)
        check_range("brightness", brightness)
        check_range("contrast", contrast)
        detail = "brightness %g, contrast %g" % (brightness, contrast)
        if not enabled or (brightness == 0 and contrast == 0):
            return (image, info_line("Brightness Contrast", enabled, mix, mask is not None, detail))
        f = contrast_factor(contrast)
        rgb = image[..., :3].to(torch.float32)
        res = (rgb - 0.5) * f + 0.5 + float(brightness) / 100.0
        out = finish_rgb(image, res, mask, mix, True)
        return (out, info_line("Brightness Contrast", True, mix, mask is not None, detail))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BrightnessContrast", SYBrightnessContrast)
NODE_DISPLAY_NAME_MAPPINGS["SYBrightnessContrast"] = "Brightness Contrast SY"
