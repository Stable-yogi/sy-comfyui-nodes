"""Levels Adjust SY: brightness, contrast, saturation and gamma in one node."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image

LUMA = (0.2126, 0.7152, 0.0722)


def _clamp(v):
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def check_levels(brightness, contrast, saturation, gamma):
    if gamma <= 0:
        raise ValueError("gamma must be above 0, got %s" % gamma)
    if contrast < 0 or saturation < 0:
        raise ValueError("contrast and saturation cannot be negative")


def adjust_pixel(rgb, brightness, contrast, saturation, gamma):
    """Pure function. rgb is three numbers 0..1. Order: gamma, contrast around grey, brightness added, then saturation."""
    check_levels(brightness, contrast, saturation, gamma)
    v = [_clamp(c) ** (1.0 / gamma) for c in rgb]
    v = [(c - 0.5) * contrast + 0.5 + brightness for c in v]
    v = [_clamp(c) for c in v]
    lum = sum(w * c for w, c in zip(LUMA, v))
    v = [lum + (c - lum) * saturation for c in v]
    return [_clamp(c) for c in v]


class SYLevelsAdjust:
    DESCRIPTION = "Brightness, contrast, saturation and gamma in one node. Default values change nothing."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to adjust."}),
                "brightness": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Adds light. Below 0 darkens, above 0 brightens."}),
                "contrast": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.01, "tooltip": "Spread between dark and light. 1 is unchanged, 0 is flat grey."}),
                "saturation": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.01, "tooltip": "Colour strength. 1 is unchanged, 0 is black and white."}),
                "gamma": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 5.0, "step": 0.01, "tooltip": "Middle tones. Above 1 brightens the shadows, below 1 darkens them."}),
            }
        }

    def run(self, image, brightness, contrast, saturation, gamma):
        import torch

        need_image(image)
        check_levels(brightness, contrast, saturation, gamma)
        rgb = min(image.shape[3], 3)
        v = image[..., :rgb].clamp(0.0, 1.0) ** (1.0 / gamma)
        v = ((v - 0.5) * contrast + 0.5 + brightness).clamp(0.0, 1.0)
        if rgb == 3:
            w = torch.tensor(LUMA, dtype=v.dtype, device=v.device)
            lum = (v * w).sum(dim=-1, keepdim=True)
            v = (lum + (v - lum) * saturation).clamp(0.0, 1.0)
        out = image.clone()
        out[..., :rgb] = v
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LevelsAdjust", SYLevelsAdjust)
NODE_DISPLAY_NAME_MAPPINGS["SYLevelsAdjust"] = "Levels Adjust SY"
