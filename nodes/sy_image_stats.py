"""Image Stats SY: measures how bright and how contrasty a picture is."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image


def check_levels(dark, bright):
    for name, v in (("dark_level", dark), ("bright_level", bright)):
        if not 0.0 <= v <= 1.0:
            raise ValueError("%s must be between 0 and 1, got %s" % (name, v))
    if not dark < bright:
        raise ValueError("dark_level (%s) must be lower than bright_level (%s)" % (dark, bright))


def luma_stats(lumas, dark, bright):
    """Pure function. lumas: list of brightness values 0..1. Returns (mean, std, dark_pct, bright_pct)."""
    check_levels(dark, bright)
    n = len(lumas)
    if n == 0:
        raise ValueError("there are no pixels to measure")
    mean = sum(lumas) / n
    var = sum((v - mean) ** 2 for v in lumas) / n
    d = sum(1 for v in lumas if v < dark)
    b = sum(1 for v in lumas if v > bright)
    return (mean, var ** 0.5, 100.0 * d / n, 100.0 * b / n)


def summary_text(mean, std, dark_pct, bright_pct):
    return "average brightness %.3f, contrast %.3f, dark pixels %.3f percent, bright pixels %.3f percent" % (mean, std, dark_pct, bright_pct)


class SYImageStats:
    DESCRIPTION = "Measures a picture: average brightness, contrast, and how many pixels are very dark or very bright."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT", "STRING")
    RETURN_NAMES = ("mean", "contrast", "dark_percent", "bright_percent", "summary")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to measure. A batch is measured as one."}),
                "dark_level": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Pixels darker than this count as dark. Must be lower than bright_level."}),
                "bright_level": ("FLOAT", {"default": 0.9, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Pixels brighter than this count as bright. Must be higher than dark_level."}),
            }
        }

    def run(self, image, dark_level, bright_level):
        import torch

        need_image(image)
        check_levels(dark_level, bright_level)
        if image.numel() == 0:
            raise ValueError("there are no pixels to measure")
        rgb = image[..., :3].to(torch.float32)
        luma = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
        mean = float(luma.mean())
        std = float(luma.std(unbiased=False))
        dark = 100.0 * float((luma < dark_level).float().mean())
        bright = 100.0 * float((luma > bright_level).float().mean())
        return (mean, std, dark, bright, summary_text(mean, std, dark, bright))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageStats", SYImageStats)
NODE_DISPLAY_NAME_MAPPINGS["SYImageStats"] = "Image Stats SY"
