"""Luminance Mask SY: makes a mask from how bright each part of a picture is."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from . import _sy_d2_common as d2
    from . import _sy_mask_math as mm
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    import _sy_d2_common as d2
    import _sy_mask_math as mm

SOURCES = ("luminance", "red", "green", "blue", "brightest channel")


def check_source(source):
    if source not in SOURCES:
        raise ValueError("source must be one of: %s, got %r" % (", ".join(SOURCES), source))


def mask_info(source, low, high, softness, invert, feather, percent):
    """Pure function. One plain line: what was measured, which band, and how much of the picture the mask covers."""
    what = "brightness" if source == "luminance" else "the %s channel" % source
    text = "Mask from %s between %g and %g" % (what, low, high)
    if softness > 0.0:
        text += " with a soft fade of %g" % softness
    if invert:
        text += ", inverted"
    if feather > 0:
        text += ", then feathered %d px" % feather
    text += ": " + d2.coverage_text(percent)
    if percent <= 0.0:
        text += ". Widen low and high, or check the invert switch"
    elif percent >= 99.99:
        text += ". The band covers the whole picture; narrow low and high"
    return text + "."


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
    DESCRIPTION = ("Builds a mask from brightness (or from one colour channel). Pixels between low and high are white in the mask, "
                   "the rest are black, with an optional soft fade and feather. The info line tells how much of the picture is selected.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "STRING")
    RETURN_NAMES = ("mask", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to measure the brightness of."}),
                "low": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Darkest brightness that still counts. 0 is black."}),
                "high": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Brightest brightness that still counts. 1 is white."}),
                "softness": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.5, "step": 0.01, "tooltip": "Width of the fade outside the band. 0 gives hard black and white."}),
                "invert": ("BOOLEAN", {"default": False, "tooltip": "Swap the mask so the chosen band becomes black."}),
            },
            "optional": {
                "source": (list(SOURCES), {"default": "luminance", "tooltip": "What to measure: overall brightness, or one colour channel (red is good for skin, blue for sky)."}),
                "feather": ("INT", {"default": 0, "min": 0, "max": mm.MAX_RADIUS, "step": 1, "tooltip": "Soften the finished mask by this many pixels, so it blends without a hard edge. 0 is off."}),
            },
        }

    def run(self, image, low, high, softness, invert, source="luminance", feather=0):
        import torch

        need_image(image)
        check_band(low, high, softness)
        check_source(source)
        if feather < 0 or feather > mm.MAX_RADIUS:
            raise ValueError("feather must be between 0 and %d" % mm.MAX_RADIUS)
        rgb = image[..., :3].to(torch.float32)
        if rgb.shape[-1] < 3:  # a grey picture: its only channel is the brightness
            y = rgb[..., 0]
        elif source == "luminance":
            y = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
        elif source == "brightest channel":
            y = rgb.amax(dim=-1)
        else:
            y = rgb[..., ("red", "green", "blue").index(source)]
        dist = torch.clamp(low - y, min=0.0) + torch.clamp(y - high, min=0.0)
        if softness > 0.0:
            m = (1.0 - dist / softness).clamp(0.0, 1.0)
        else:
            m = (dist <= 0.0).to(torch.float32)
        if invert:
            m = 1.0 - m
        if feather > 0:
            m = mm.t_blur(m, int(feather))
        m = m.contiguous()
        return (m, mask_info(source, low, high, softness, bool(invert), int(feather), 100.0 * float(m.mean())))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LuminanceMask", SYLuminanceMask)
NODE_DISPLAY_NAME_MAPPINGS["SYLuminanceMask"] = "Luminance Mask SY"
