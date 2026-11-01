"""Posterize SY: cuts every colour channel down to a few flat levels."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from ._sy_d3_info import need_nonempty
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    from _sy_d3_info import need_nonempty


def check_levels(levels):
    if levels < 2 or levels > 256:
        raise ValueError("levels must be between 2 and 256, got %s" % levels)


def quantise(v, levels):
    """Pure function. Snaps one channel value 0..1 to the nearest of `levels` steps (halves round up)."""
    check_levels(levels)
    v = 0.0 if v < 0.0 else 1.0 if v > 1.0 else v
    steps = levels - 1
    return int(v * steps + 0.5) / float(steps)


def posterize_info(levels):
    """Pure function. Plain sentence: how many steps per channel and the most colours the picture can have now."""
    check_levels(levels)
    steps = [("%.2f" % (i / float(levels - 1))) for i in range(levels)]
    shown = ", ".join(steps) if levels <= 6 else "%s ... %s" % (", ".join(steps[:3]), steps[-1])
    text = "%d levels per colour channel (values %s), so at most %d different colours." % (levels, shown, levels ** 3)
    if levels >= 128:
        text += " That many levels looks almost like the original: lower levels for a visible poster look."
    return text


class SYPosterize:
    DESCRIPTION = "Reduces each colour channel to a small number of flat levels for a poster or cartoon look. The info output lists the steps kept and the most colours left."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to flatten into fewer colours."}),
                "levels": ("INT", {"default": 4, "min": 2, "max": 256, "tooltip": "How many brightness steps each colour channel keeps. 2 is the harshest."}),
            }
        }

    def run(self, image, levels):
        import torch

        need_image(image)
        need_nonempty(image.shape)
        check_levels(levels)
        steps = float(levels - 1)
        out = image.clone()
        rgb = min(image.shape[3], 3)
        v = image[..., :rgb].clamp(0.0, 1.0)
        out[..., :rgb] = torch.floor(v * steps + 0.5) / steps
        return (out, posterize_info(int(levels)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Posterize", SYPosterize)
