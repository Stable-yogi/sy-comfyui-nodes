"""Brightness Contrast SY: makes a picture lighter or darker and flatter or punchier."""
import math

try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image


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
    DESCRIPTION = "Makes a picture lighter or darker, and flatter or punchier. Both at 0 leaves the picture as it is."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to change."}),
                "brightness": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "tooltip": "Below 0 darkens, above 0 lightens."}),
                "contrast": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "tooltip": "Below 0 flattens the picture, above 0 pushes lights and darks apart."}),
            }
        }

    def run(self, image, brightness, contrast):
        import torch

        need_image(image)
        check_range("brightness", brightness)
        check_range("contrast", contrast)
        if brightness == 0 and contrast == 0:
            return (image,)
        f = contrast_factor(contrast)
        rgb = image[..., :3].to(torch.float32)
        res = ((rgb - 0.5) * f + 0.5 + float(brightness) / 100.0).clamp(0.0, 1.0)
        out = image.clone()
        out[..., :3] = res.to(image.dtype)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BrightnessContrast", SYBrightnessContrast)
NODE_DISPLAY_NAME_MAPPINGS["SYBrightnessContrast"] = "Brightness Contrast SY"
