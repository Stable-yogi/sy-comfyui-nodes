"""Luminance Mask SY: makes a mask from how bright each part of a picture is."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image


def check_band(low, high, softness):
    if not 0.0 <= low <= 1.0 or not 0.0 <= high <= 1.0:
        raise ValueError("low and high must be between 0 and 1, got %s and %s" % (low, high))
    if low > high:
        raise ValueError("low must not be above high (got low %s, high %s)" % (low, high))
    if not 0.0 <= softness <= 0.5:
        raise ValueError("softness must be between 0 and 0.5, got %s" % softness)


def band_value(luma, low, high, softness):
    """Pure function. 1 when luma sits inside [low, high], fading linearly to 0 over `softness` outside each end."""
    check_band(low, high, softness)
    if luma < low:
        dist = low - luma
    elif luma > high:
        dist = luma - high
    else:
        return 1.0
    if softness <= 0.0:
        return 0.0
    v = 1.0 - dist / softness
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


class SYLuminanceMask:
    DESCRIPTION = "Builds a mask from brightness. Pixels between low and high are white in the mask, the rest are black, with an optional soft fade."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to measure the brightness of."}),
                "low": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Darkest brightness that still counts. 0 is black."}),
                "high": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Brightest brightness that still counts. 1 is white."}),
                "softness": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.5, "step": 0.01, "tooltip": "Width of the fade outside the band. 0 gives hard black and white."}),
                "invert": ("BOOLEAN", {"default": False, "tooltip": "Swap the mask so the chosen band becomes black."}),
            }
        }

    def run(self, image, low, high, softness, invert):
        import torch

        need_image(image)
        check_band(low, high, softness)
        rgb = image[..., :3].to(torch.float32)
        y = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
        dist = torch.clamp(low - y, min=0.0) + torch.clamp(y - high, min=0.0)
        if softness > 0.0:
            m = (1.0 - dist / softness).clamp(0.0, 1.0)
        else:
            m = (dist <= 0.0).to(torch.float32)
        if invert:
            m = 1.0 - m
        return (m.contiguous(),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LuminanceMask", SYLuminanceMask)
NODE_DISPLAY_NAME_MAPPINGS["SYLuminanceMask"] = "Luminance Mask SY"
