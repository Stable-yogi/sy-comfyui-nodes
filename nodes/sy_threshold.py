"""Threshold SY: turns a picture into pure black and white (or a soft ramp) around a brightness level."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image


def check_params(level, softness):
    if not 0.0 <= level <= 1.0:
        raise ValueError("level must be between 0 and 1, got %s" % level)
    if not 0.0 <= softness <= 0.5:
        raise ValueError("softness must be between 0 and 0.5, got %s" % softness)


def threshold_value(luma, level, softness):
    """Pure function. 1 at or above level, 0 below (hard). With softness s > 0: linear ramp from level-s (0) to level+s (1)."""
    check_params(level, softness)
    if softness <= 0.0:
        return 1.0 if luma >= level else 0.0
    v = (luma - (level - softness)) / (2.0 * softness)
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


class SYThreshold:
    DESCRIPTION = "Makes a black and white picture: brighter than the level becomes white, darker becomes black. Also gives a mask."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to turn black and white."}),
                "level": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Brightness where black turns to white. Higher means more of the picture goes black."}),
                "softness": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.5, "step": 0.01, "tooltip": "Width of a smooth grey ramp around the level. 0 gives a hard edge."}),
                "invert": ("BOOLEAN", {"default": False, "tooltip": "Swap black and white."}),
            }
        }

    def run(self, image, level, softness, invert):
        import torch

        need_image(image)
        check_params(level, softness)
        rgb = image[..., :3].to(torch.float32)
        luma = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
        if softness <= 0.0:
            v = (luma >= level).to(torch.float32)
        else:
            v = ((luma - (level - softness)) / (2.0 * softness)).clamp(0.0, 1.0)
        if invert:
            v = 1.0 - v
        v = v.to(image.dtype)
        img = v.unsqueeze(-1).expand(-1, -1, -1, 3).contiguous()
        return (img, v.contiguous())


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Threshold", SYThreshold)
