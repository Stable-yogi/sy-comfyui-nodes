"""Solarize SY: flips every colour value that is at or above a threshold, for a film-darkroom look."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image


def check_threshold(threshold):
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1, got %s" % threshold)


def solarize_value(v, threshold):
    """Pure function. A value at or above the threshold becomes 1 - v; a lower one stays."""
    check_threshold(threshold)
    return 1.0 - v if v >= threshold else v


class SYSolarize:
    DESCRIPTION = "Flips every colour value that is above a limit, like a darkroom solarize effect. Alpha is left alone."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to change."}),
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Colour values at or above this limit are flipped. 0.5 is the classic look."}),
            }
        }

    def run(self, image, threshold):
        import torch

        need_image(image)
        check_threshold(threshold)
        rgb = image[..., :3]
        res = torch.where(rgb >= threshold, 1.0 - rgb, rgb)
        out = image.clone()
        out[..., :3] = res
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Solarize", SYSolarize)
