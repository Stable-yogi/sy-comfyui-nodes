"""Grayscale SY: turns a picture into shades of grey, with a choice of how brightness is measured."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image

METHODS = ("rec709", "rec601", "average", "lightness")


def check_method(method):
    if method not in METHODS:
        raise ValueError("method must be one of: %s, got %r" % (", ".join(METHODS), method))


def check_strength(strength):
    if not 0.0 <= strength <= 1.0:
        raise ValueError("strength must be between 0 and 1, got %s" % strength)


def grey_value(r, g, b, method):
    """Pure function. Grey brightness of one pixel by the chosen method."""
    check_method(method)
    if method == "rec709":
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    if method == "rec601":
        return 0.299 * r + 0.587 * g + 0.114 * b
    if method == "average":
        return (r + g + b) / 3.0
    return (max(r, g, b) + min(r, g, b)) / 2.0


def grayscale_pixel(rgb, method, strength):
    """Pure function. Blend of the original pixel and its grey version."""
    check_strength(strength)
    g = grey_value(rgb[0], rgb[1], rgb[2], method)
    return tuple(rgb[i] + (g - rgb[i]) * strength for i in range(3))


class SYGrayscale:
    DESCRIPTION = "Turns a picture into shades of grey. Pick how brightness is measured and how strong the effect is."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to turn grey."}),
                "method": (list(METHODS), {"default": "rec709", "tooltip": "How brightness is measured. rec709 matches how the eye sees modern screens; lightness keeps contrast flat."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "0 keeps the colours, 1 is fully grey."}),
            }
        }

    def run(self, image, method, strength):
        import torch

        need_image(image)
        check_method(method)
        check_strength(strength)
        rgb = image[..., :3].to(torch.float32)
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        if method == "rec709":
            grey = 0.2126 * r + 0.7152 * g + 0.0722 * b
        elif method == "rec601":
            grey = 0.299 * r + 0.587 * g + 0.114 * b
        elif method == "average":
            grey = (r + g + b) / 3.0
        else:
            grey = (rgb.max(dim=-1).values + rgb.min(dim=-1).values) / 2.0
        grey3 = grey.unsqueeze(-1).expand(-1, -1, -1, 3)
        out = image.clone()
        out[..., :3] = (rgb + (grey3 - rgb) * float(strength)).to(image.dtype)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Grayscale", SYGrayscale)
