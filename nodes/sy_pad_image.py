"""Pad Image SY: adds margins around a picture and gives a mask of the new area, for outpainting."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import COLOUR_NAMES, CUSTOM_TIP, need_image, parse_colour
    from ._sy_d3_info import need_nonempty, size_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import COLOUR_NAMES, CUSTOM_TIP, need_image, parse_colour
    from _sy_d3_info import need_nonempty, size_text

BIG_MEGAPIXELS = 16.0


def snap_extra(total, multiple):
    """Pure function. Pixels to add so that `total` becomes a multiple of `multiple` (0 when it already is)."""
    if multiple < 1:
        raise ValueError("multiple_of must be 1 or more, got %s" % multiple)
    return (-int(total)) % int(multiple)


def pad_info(width, height, left, right, top, bottom, extra_x=0, extra_y=0):
    """Pure function. Plain sentence. `right`/`bottom` already include the extra pixels added to reach a multiple."""
    nw, nh = padded_size(width, height, left, right, top, bottom)
    text = "Padded %s to %s (left %d, right %d, top %d, bottom %d)." % (size_text(width, height), size_text(nw, nh), left, right, top, bottom)
    if extra_x or extra_y:
        text += " Added %d px right and %d px bottom extra so the size is a multiple of the chosen number." % (extra_x, extra_y)
    mp = nw * nh / 1e6
    if mp > BIG_MEGAPIXELS:
        text += " The result is %.1f megapixels: this may be too big for your graphics card." % mp
    return text


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
    DESCRIPTION = "Adds space around a picture. Also gives a mask that is white on the new space, ready for outpainting. Can round the new size up to a multiple of 8 or 64, and the info output tells the old and new size."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT", "STRING")
    RETURN_NAMES = ("image", "mask", "width", "height", "info")

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
                "multiple_of": ("INT", {"default": 1, "min": 1, "max": 512, "step": 1, "tooltip": "Round the new width and height up to a multiple of this, for example 8. Extra goes right and bottom."}),
            },
        }

    def run(self, image, left, right, top, bottom, color, custom_color="", multiple_of=1):
        import torch

        need_image(image)
        need_nonempty(image.shape)
        b, h, w, c = image.shape
        nw0, nh0 = padded_size(w, h, left, right, top, bottom)
        extra_x = snap_extra(nw0, multiple_of)
        extra_y = snap_extra(nh0, multiple_of)
        right += extra_x
        bottom += extra_y
        nw, nh = padded_size(w, h, left, right, top, bottom)
        rgb = parse_colour(color, custom_color)
        fill = [rgb[i] if i < 3 else 1.0 for i in range(c)]
        canvas = torch.tensor(fill, dtype=image.dtype, device=image.device).view(1, 1, 1, c).expand(b, nh, nw, c).clone()
        canvas[:, top:top + h, left:left + w, :] = image
        mask = torch.ones((b, nh, nw), dtype=image.dtype, device=image.device)
        mask[:, top:top + h, left:left + w] = 0.0
        return (canvas, mask, nw, nh, pad_info(w, h, left, right, top, bottom, extra_x, extra_y))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PadImage", SYPadImage)
NODE_DISPLAY_NAME_MAPPINGS["SYPadImage"] = "Pad Image SY"
