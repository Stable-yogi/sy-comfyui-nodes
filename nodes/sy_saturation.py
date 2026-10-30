"""Saturation SY: makes colours stronger or weaker, either evenly or by lifting only the dull colours."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image

MODES = ("saturation", "vibrance")


def check_mode(mode):
    if mode not in MODES:
        raise ValueError("mode must be one of: %s, got %r" % (", ".join(MODES), mode))


def check_amount(amount):
    if not -100.0 <= amount <= 100.0:
        raise ValueError("amount must be between -100 and 100, got %s" % amount)


def saturate_pixel(r, g, b, amount, mode):
    """Pure function. One pixel, values 0..1. amount 0 returns the pixel unchanged."""
    check_mode(mode)
    check_amount(amount)
    if amount == 0:
        return (r, g, b)
    grey = 0.2126 * r + 0.7152 * g + 0.0722 * b
    k = amount / 100.0
    if mode == "saturation":
        factor = 1.0 + k
    else:
        factor = 1.0 + k * (1.0 - (max(r, g, b) - min(r, g, b)))
    out = []
    for v in (r, g, b):
        o = grey + (v - grey) * factor
        out.append(0.0 if o < 0.0 else 1.0 if o > 1.0 else o)
    return tuple(out)


class SYSaturation:
    DESCRIPTION = "Makes colours stronger or weaker. Vibrance mostly lifts dull colours and leaves strong ones alone."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to change."}),
                "amount": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "tooltip": "Below 0 fades the colour, -100 is grey. Above 0 makes colours stronger."}),
                "mode": (list(MODES), {"default": "saturation", "tooltip": "saturation changes every colour the same; vibrance moves dull colours more than strong ones."}),
            }
        }

    def run(self, image, amount, mode):
        import torch

        need_image(image)
        check_mode(mode)
        check_amount(amount)
        if amount == 0:
            return (image,)
        rgb = image[..., :3].to(torch.float32)
        grey = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).unsqueeze(-1)
        k = float(amount) / 100.0
        if mode == "saturation":
            factor = 1.0 + k
        else:
            s = (rgb.max(dim=-1).values - rgb.min(dim=-1).values).unsqueeze(-1)
            factor = 1.0 + k * (1.0 - s)
        res = (grey + (rgb - grey) * factor).clamp(0.0, 1.0)
        out = image.clone()
        out[..., :3] = res.to(image.dtype)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Saturation", SYSaturation)
