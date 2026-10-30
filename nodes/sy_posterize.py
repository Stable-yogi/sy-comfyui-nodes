"""Posterize SY: cuts every colour channel down to a few flat levels."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image


def check_levels(levels):
    if levels < 2 or levels > 256:
        raise ValueError("levels must be between 2 and 256, got %s" % levels)


def quantise(v, levels):
    """Pure function. Snaps one channel value 0..1 to the nearest of `levels` steps (halves round up)."""
    check_levels(levels)
    v = 0.0 if v < 0.0 else 1.0 if v > 1.0 else v
    steps = levels - 1
    return int(v * steps + 0.5) / float(steps)


class SYPosterize:
    DESCRIPTION = "Reduces each colour channel to a small number of flat levels for a poster or cartoon look."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

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
        check_levels(levels)
        steps = float(levels - 1)
        out = image.clone()
        rgb = min(image.shape[3], 3)
        v = image[..., :rgb].clamp(0.0, 1.0)
        out[..., :rgb] = torch.floor(v * steps + 0.5) / steps
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Posterize", SYPosterize)
