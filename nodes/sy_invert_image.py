"""Invert Image SY: flips the colours of a picture, all of them or just one channel."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from . import _sy_d2_common as d2
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    import _sy_d2_common as d2

CHANNELS = ("rgb", "red", "green", "blue")
FLAGS = {"rgb": (True, True, True), "red": (True, False, False), "green": (False, True, False), "blue": (False, False, True)}


def check_channels(channels):
    if channels not in CHANNELS:
        raise ValueError("channels must be one of: %s, got %r" % (", ".join(CHANNELS), channels))


def invert_pixel(r, g, b, channels):
    """Pure function. Returns (r, g, b) with 1 - value on the chosen channels only."""
    check_channels(channels)
    f = FLAGS[channels]
    return (1.0 - r if f[0] else r, 1.0 - g if f[1] else g, 1.0 - b if f[2] else b)


def invert_info(channels, note=""):
    """Pure function. One plain line about what was inverted."""
    check_channels(channels)
    what = "all colours" if channels == "rgb" else "the %s channel only" % channels
    return d2.join_info(["Inverted %s" % what, note]) + "."


class SYInvertImage:
    DESCRIPTION = ("Inverts the colours of a picture like a photo negative. Can invert only red, green or blue. "
                   "Transparency is left alone. Add a mask to invert only part of the picture.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to invert."}),
                "channels": (list(CHANNELS), {"default": "rgb", "tooltip": "Which colours to flip. rgb flips all three; red, green or blue flips just that one."}),
            },
            "optional": {
                "mask": ("MASK", {"tooltip": "Optional. Change only where this mask is white. A different size is stretched to fit."}),
            },
        }

    def run(self, image, channels, mask=None):
        import torch

        need_image(image)
        d2.need_rgb(image, "Invert Image")
        check_channels(channels)
        out = image.clone()
        for i, on in enumerate(FLAGS[channels]):
            if on:
                out[..., i] = 1.0 - image[..., i]
        out, note = d2.t_apply_with_mask(image, out, mask)
        return (out, invert_info(channels, note))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "InvertImage", SYInvertImage)
NODE_DISPLAY_NAME_MAPPINGS["SYInvertImage"] = "Invert Image SY"
