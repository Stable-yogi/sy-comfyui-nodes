"""Pad Image SY: adds margins around a picture and gives a mask of the new area, for outpainting."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import COLOUR_NAMES, CUSTOM_TIP, need_image, parse_colour
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import COLOUR_NAMES, CUSTOM_TIP, need_image, parse_colour


def padded_size(width, height, left, right, top, bottom):
    """Pure function. Returns the new (width, height)."""
    if min(left, right, top, bottom) < 0:
        raise ValueError("margins cannot be negative")
    if min(width, height) < 1:
        raise ValueError("picture size must be at least 1x1")
    return (width + left + right, height + top + bottom)


def padded_mask(width, height, left, right, top, bottom):
    """Pure function. Nested lists [H][W]: 1.0 on the new margin, 0.0 where the old picture sits."""
    nw, nh = padded_size(width, height, left, right, top, bottom)
    return [[0.0 if (top <= y < top + height and left <= x < left + width) else 1.0 for x in range(nw)] for y in range(nh)]


class SYPadImage:
    DESCRIPTION = "Adds space around a picture. Also gives a mask that is white on the new space, ready for outpainting."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("image", "mask", "width", "height")

    @classmethod
    def INPUT_TYPES(cls):
        m = {"default": 0, "min": 0, "max": 8192}
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to add space around."}),
                "left": ("INT", dict(m, tooltip="Pixels to add on the left.")),
                "right": ("INT", dict(m, tooltip="Pixels to add on the right.")),
                "top": ("INT", dict(m, tooltip="Pixels to add on the top.")),
                "bottom": ("INT", dict(m, tooltip="Pixels to add at the bottom.")),
                "color": (list(COLOUR_NAMES), {"default": "grey", "tooltip": "Colour that fills the new space."}),
            },
            "optional": {
                "custom_color": ("STRING", {"default": "", "tooltip": CUSTOM_TIP}),
            },
        }

    def run(self, image, left, right, top, bottom, color, custom_color=""):
        import torch

        need_image(image)
        b, h, w, c = image.shape
        nw, nh = padded_size(w, h, left, right, top, bottom)
        rgb = parse_colour(color, custom_color)
        fill = [rgb[i] if i < 3 else 1.0 for i in range(c)]
        canvas = torch.tensor(fill, dtype=image.dtype, device=image.device).view(1, 1, 1, c).expand(b, nh, nw, c).clone()
        canvas[:, top:top + h, left:left + w, :] = image
        mask = torch.ones((b, nh, nw), dtype=image.dtype, device=image.device)
        mask[:, top:top + h, left:left + w] = 0.0
        return (canvas, mask, nw, nh)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PadImage", SYPadImage)
NODE_DISPLAY_NAME_MAPPINGS["SYPadImage"] = "Pad Image SY"
