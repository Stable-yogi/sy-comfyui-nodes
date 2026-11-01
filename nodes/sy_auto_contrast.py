"""Auto Contrast SY: stretches the darkest and brightest values of each picture to fill the full range."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import clamp01, need_image
    from ._sy_d1_finish import MASK_TIP, MIX_TIP, ENABLED_TIP, finish_rgb, info_line
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import clamp01, need_image
    from _sy_d1_finish import MASK_TIP, MIX_TIP, ENABLED_TIP, finish_rgb, info_line


def check_clip(clip_percent):
    if not 0.0 <= clip_percent <= 20.0:
        raise ValueError("clip_percent must be between 0 and 20, got %s" % clip_percent)


def clip_indexes(count, clip_percent):
    """Pure function. Positions of the low and high percentile in a sorted list of `count` values."""
    check_clip(clip_percent)
    if count < 1:
        raise ValueError("picture has no pixels")
    cut = int(clip_percent / 100.0 * (count - 1))
    return cut, count - 1 - cut


def stretch_range(lumas_sorted, clip_percent):
    """Pure function. Returns (low, high) from a sorted list of luma values."""
    lo, hi = clip_indexes(len(lumas_sorted), clip_percent)
    return lumas_sorted[lo], lumas_sorted[hi]


def stretch_value(v, low, high):
    """Pure function. Linear stretch of one value, clamped to 0..1. A flat range returns v unchanged."""
    if high - low < 1e-6:
        return v
    return clamp01((v - low) / (high - low))


class SYAutoContrast:
    DESCRIPTION = ("Stretches the darkest and brightest parts of each picture to fill the full range. Fixes dull, flat pictures. "
                   "Adds per-colour stretching (removes colour casts), a mask, a mix slider, an on/off switch and an info line.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to change. Each picture is handled on its own."}),
                "clip_percent": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 20.0, "step": 0.1, "tooltip": "Percent of the darkest and brightest pixels to ignore when finding the range."}),
            },
            "optional": {
                "mask": ("MASK", {"tooltip": MASK_TIP}),
                "mix": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": MIX_TIP}),
                "enabled": ("BOOLEAN", {"default": True, "tooltip": ENABLED_TIP}),
                "per_colour": ("BOOLEAN", {"default": False, "tooltip": "On: stretch red, green and blue on their own. Also removes a colour cast."}),
            },
        }

    def run(self, image, clip_percent, mask=None, mix=1.0, enabled=True, per_colour=False):
        import torch

        need_image(image)
        check_clip(clip_percent)
        detail = "clip %g%%, %s" % (clip_percent, "per colour" if per_colour else "by brightness")
        if not enabled:
            return (image, info_line("Auto Contrast", False, mix, mask is not None))
        count = image.shape[1] * image.shape[2]
        lo_i, hi_i = clip_indexes(count, clip_percent)
        new = image[..., :3].to(torch.float32).clone()
        flat_pictures = 0
        for i in range(image.shape[0]):
            rgb = image[i, ..., :3].to(torch.float32)
            if per_colour:
                for c in range(3):
                    srt = torch.sort(rgb[..., c].flatten()).values
                    low, high = float(srt[lo_i]), float(srt[hi_i])
                    if high - low >= 1e-6:
                        new[i, ..., c] = (rgb[..., c] - low) / (high - low)
                continue
            luma = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).flatten()
            srt = torch.sort(luma).values
            low, high = float(srt[lo_i]), float(srt[hi_i])
            if high - low < 1e-6:
                flat_pictures += 1
                continue
            new[i] = (rgb - low) / (high - low)
        out = finish_rgb(image, new, mask, mix, True)
        if flat_pictures:
            detail += ", %d flat picture(s) left as they are" % flat_pictures
        return (out, info_line("Auto Contrast", True, mix, mask is not None, detail))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AutoContrast", SYAutoContrast)
NODE_DISPLAY_NAME_MAPPINGS["SYAutoContrast"] = "Auto Contrast SY"
