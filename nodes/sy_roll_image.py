"""Roll Image SY: slides a picture sideways or up and down and wraps what falls off one edge back in on the other."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image

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


class SYRollImage:
    DESCRIPTION = "Slides a picture and wraps whatever leaves one edge back in on the opposite edge. Handy for checking seamless textures."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to slide."}),
                "shift_x": ("INT", {"default": 0, "min": -8192, "max": 8192, "step": 1, "tooltip": "Sideways move. Positive moves the picture to the right."}),
                "shift_y": ("INT", {"default": 0, "min": -8192, "max": 8192, "step": 1, "tooltip": "Up and down move. Positive moves the picture down."}),
                "unit": (list(UNITS), {"default": "pixels", "tooltip": "pixels moves by that many pixels; percent moves by a share of the width and height."}),
            }
        }

    def run(self, image, shift_x, shift_y, unit):
        import torch

        need_image(image)
        check_unit(unit)
        b, h, w, c = image.shape
        sx = shift_pixels(shift_x, unit, w) % w
        sy = shift_pixels(shift_y, unit, h) % h
        if sx == 0 and sy == 0:
            return (image,)
        return (torch.roll(image, shifts=(sy, sx), dims=(1, 2)).contiguous(),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RollImage", SYRollImage)
NODE_DISPLAY_NAME_MAPPINGS["SYRollImage"] = "Roll Image SY"
