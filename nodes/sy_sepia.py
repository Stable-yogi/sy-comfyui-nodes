"""Sepia SY: gives a picture the warm brown tone of an old photo."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import clamp01, need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import clamp01, need_image

MATRIX = (
    (0.393, 0.769, 0.189),
    (0.349, 0.686, 0.168),
    (0.272, 0.534, 0.131),
)


def check_strength(strength):
    if not 0.0 <= strength <= 1.0:
        raise ValueError("strength must be between 0 and 1, got %s" % strength)


def sepia_pixel(r, g, b, strength):
    """Pure function. One pixel, values 0..1. strength 0 returns the pixel exactly."""
    check_strength(strength)
    if strength == 0:
        return (r, g, b)
    out = []
    for row, orig in zip(MATRIX, (r, g, b)):
        s = clamp01(row[0] * r + row[1] * g + row[2] * b)
        out.append(orig + (s - orig) * strength)
    return tuple(out)


class SYSepia:
    DESCRIPTION = "Gives a picture the warm brown tone of an old photograph. Strength blends from the original to full sepia."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to change."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "0 keeps the original, 1 is full sepia."}),
            }
        }

    def run(self, image, strength):
        import torch

        need_image(image)
        check_strength(strength)
        if strength == 0:
            return (image,)
        rgb = image[..., :3]
        m = torch.tensor(MATRIX, dtype=rgb.dtype, device=rgb.device)
        sep = torch.matmul(rgb, m.t()).clamp(0.0, 1.0)
        res = rgb + (sep - rgb) * float(strength)
        out = image.clone()
        out[..., :3] = res
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Sepia", SYSepia)
