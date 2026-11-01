"""Levels Adjust SY: brightness, contrast, saturation and gamma in one node."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from . import _sy_d2_common as d2
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    import _sy_d2_common as d2

LUMA = (0.2126, 0.7152, 0.0722)


def _clamp(v):
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def check_levels(brightness, contrast, saturation, gamma, black_point=0.0, white_point=1.0):
    if gamma <= 0:
        raise ValueError("gamma must be above 0, got %s" % gamma)
    if contrast < 0 or saturation < 0:
        raise ValueError("contrast and saturation cannot be negative")
    if not (0.0 <= black_point <= 1.0 and 0.0 <= white_point <= 1.0):
        raise ValueError("black_point and white_point must be between 0 and 1, got %s and %s" % (black_point, white_point))
    if black_point >= white_point:
        raise ValueError("black_point (%s) must be lower than white_point (%s): the picture cannot be stretched between them" % (black_point, white_point))


def adjust_pixel(rgb, brightness, contrast, saturation, gamma, black_point=0.0, white_point=1.0):
    """Pure function. rgb is three numbers 0..1. Order: black/white point stretch, gamma, contrast around grey,
    brightness added, then saturation. The default black 0 and white 1 change nothing."""
    check_levels(brightness, contrast, saturation, gamma, black_point, white_point)
    span = white_point - black_point
    v = [_clamp((_clamp(c) - black_point) / span) ** (1.0 / gamma) for c in rgb]
    v = [(c - 0.5) * contrast + 0.5 + brightness for c in v]
    v = [_clamp(c) for c in v]
    lum = sum(w * c for w, c in zip(LUMA, v))
    v = [lum + (c - lum) * saturation for c in v]
    return [_clamp(c) for c in v]


def levels_info(brightness, contrast, saturation, gamma, black_point, white_point, note=""):
    """Pure function. Lists only the settings that changed something."""
    parts = []
    if black_point > 0.0 or white_point < 1.0:
        parts.append("black point %g, white point %g" % (black_point, white_point))
    if gamma != 1.0:
        parts.append("gamma %g" % gamma)
    if contrast != 1.0:
        parts.append("contrast %g" % contrast)
    if brightness != 0.0:
        parts.append("brightness %+g" % brightness)
    if saturation != 1.0:
        parts.append("saturation %g" % saturation)
    head = "Applied " + ", ".join(parts) if parts else "All settings are at their neutral values: the picture was not changed"
    return d2.join_info([head, note]) + "."


class SYLevelsAdjust:
    DESCRIPTION = ("Black point, white point, gamma, contrast, brightness and saturation in one node. Default values change nothing. "
                   "Add a mask to adjust only one area. The info line lists what was changed.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to adjust."}),
                "brightness": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Adds light. Below 0 darkens, above 0 brightens."}),
                "contrast": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.01, "tooltip": "Spread between dark and light. 1 is unchanged, 0 is flat grey."}),
                "saturation": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.01, "tooltip": "Colour strength. 1 is unchanged, 0 is black and white."}),
                "gamma": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 5.0, "step": 0.01, "tooltip": "Middle tones. Above 1 brightens the shadows, below 1 darkens them."}),
            },
            "optional": {
                "black_point": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.99, "step": 0.01, "tooltip": "Brightness that becomes pure black, for example 0.05. Fixes washed-out shadows."}),
                "white_point": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 1.0, "step": 0.01, "tooltip": "Brightness that becomes pure white, for example 0.95. Fixes dull highlights."}),
                "mask": ("MASK", {"tooltip": "Optional. Adjust only where this mask is white. A different size is stretched to fit."}),
            },
        }

    def run(self, image, brightness, contrast, saturation, gamma, black_point=0.0, white_point=1.0, mask=None):
        import torch

        need_image(image)
        check_levels(brightness, contrast, saturation, gamma, black_point, white_point)
        rgb = min(image.shape[3], 3)
        v = ((image[..., :rgb].clamp(0.0, 1.0) - black_point) / (white_point - black_point)).clamp(0.0, 1.0) ** (1.0 / gamma)
        v = ((v - 0.5) * contrast + 0.5 + brightness).clamp(0.0, 1.0)
        if rgb == 3:
            w = torch.tensor(LUMA, dtype=v.dtype, device=v.device)
            lum = (v * w).sum(dim=-1, keepdim=True)
            v = (lum + (v - lum) * saturation).clamp(0.0, 1.0)
        out = image.clone()
        out[..., :rgb] = v
        out, note = d2.t_apply_with_mask(image, out, mask)
        return (out, levels_info(brightness, contrast, saturation, gamma, black_point, white_point, note))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LevelsAdjust", SYLevelsAdjust)
NODE_DISPLAY_NAME_MAPPINGS["SYLevelsAdjust"] = "Levels Adjust SY"
