"""Auto Contrast SY: stretches the darkest and brightest values of each picture to fill the full range."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import clamp01, need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import clamp01, need_image


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
    DESCRIPTION = "Stretches the darkest and brightest parts of each picture to fill the full range. Fixes dull, flat pictures."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to change. Each picture is handled on its own."}),
                "clip_percent": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 20.0, "step": 0.1, "tooltip": "Percent of the darkest and brightest pixels to ignore when finding the range."}),
            }
        }

    def run(self, image, clip_percent):
        import torch

        need_image(image)
        check_clip(clip_percent)
        out = image.clone()
        count = image.shape[1] * image.shape[2]
        lo_i, hi_i = clip_indexes(count, clip_percent)
        for i in range(image.shape[0]):
            rgb = image[i, ..., :3].to(torch.float32)
            luma = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).flatten()
            srt = torch.sort(luma).values
            low, high = float(srt[lo_i]), float(srt[hi_i])
            if high - low < 1e-6:
                continue
            out[i, ..., :3] = ((rgb - low) / (high - low)).clamp(0.0, 1.0).to(image.dtype)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AutoContrast", SYAutoContrast)
NODE_DISPLAY_NAME_MAPPINGS["SYAutoContrast"] = "Auto Contrast SY"
