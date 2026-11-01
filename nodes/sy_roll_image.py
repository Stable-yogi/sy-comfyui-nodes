"""Roll Image SY: slides a picture sideways or up and down and wraps what falls off one edge back in on the other."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from ._sy_d3_info import need_nonempty
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    from _sy_d3_info import need_nonempty

UNITS = ("pixels", "percent")


def check_unit(unit):
    if unit not in UNITS:
        raise ValueError("unit must be one of: %s, got %r" % (", ".join(UNITS), unit))


def roll_index(i, shift, size):
    """Pure function. Where the pixel that sits at position i ends up when content moves by `shift` with wrap-around."""
    if size < 1:
        raise ValueError("size must be at least 1, got %s" % size)
    return (i + shift) % size


def shift_pixels(shift, unit, size):
    """Pure function. Shift in pixels for a side of `size` pixels. Percent is a percent of that side."""
    check_unit(unit)
    if unit == "percent":
        return int(round(shift * size / 100.0))
    return int(shift)


def roll_amounts(shift_x, shift_y, unit, width, height, half_offset=False):
    """Pure function. Final move in pixels (sx, sy), each wrapped into 0..size-1. half_offset adds half the width and height
    (the classic way to look at the seams of a tileable texture)."""
    check_unit(unit)
    if width < 1 or height < 1:
        raise ValueError("picture size must be at least 1x1")
    sx = shift_pixels(shift_x, unit, width)
    sy = shift_pixels(shift_y, unit, height)
    if half_offset:
        sx += width // 2
        sy += height // 2
    return sx % width, sy % height


def roll_info(sx, sy, width, height, half_offset=False):
    """Pure function. Plain sentence for a move already wrapped by roll_amounts."""
    if sx == 0 and sy == 0:
        return "No move: the picture was passed through unchanged."
    parts = []
    if sx:
        parts.append("%d px to the right" % sx)
    if sy:
        parts.append("%d px down" % sy)
    text = "Moved the picture " + " and ".join(parts) + ", what left one edge came back on the other"
    if half_offset:
        text += " (half-size offset on, seams of a tileable picture now sit in the middle)"
    return text + "."


class SYRollImage:
    DESCRIPTION = "Slides a picture and wraps whatever leaves one edge back in on the opposite edge. Handy for checking seamless textures: switch on half_offset to push the seams into the middle. The info output tells the real move."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to slide."}),
                "shift_x": ("INT", {"default": 0, "min": -8192, "max": 8192, "step": 1, "tooltip": "Sideways move. Positive moves the picture to the right."}),
                "shift_y": ("INT", {"default": 0, "min": -8192, "max": 8192, "step": 1, "tooltip": "Up and down move. Positive moves the picture down."}),
                "unit": (list(UNITS), {"default": "pixels", "tooltip": "pixels moves by that many pixels; percent moves by a share of the width and height."}),
            },
            "optional": {
                "half_offset": ("BOOLEAN", {"default": False, "tooltip": "On: also move by half the width and height, to show the seams of a tileable texture in the middle."}),
            },
        }

    def run(self, image, shift_x, shift_y, unit, half_offset=False):
        import torch

        need_image(image)
        need_nonempty(image.shape)
        check_unit(unit)
        b, h, w, c = image.shape
        sx, sy = roll_amounts(shift_x, shift_y, unit, w, h, bool(half_offset))
        info = roll_info(sx, sy, w, h, bool(half_offset))
        if sx == 0 and sy == 0:
            return (image, info)
        return (torch.roll(image, shifts=(sy, sx), dims=(1, 2)).contiguous(), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RollImage", SYRollImage)
NODE_DISPLAY_NAME_MAPPINGS["SYRollImage"] = "Roll Image SY"
