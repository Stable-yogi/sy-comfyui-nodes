"""Channel Split SY: pulls the red, green, blue and transparency channels of a picture out as four masks."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image


def split_pixel(pixel):
    """Pure function. A pixel of 3 or 4 values -> (r, g, b, a); a is 1.0 when the pixel has no alpha."""
    if len(pixel) not in (3, 4):
        raise ValueError("a pixel needs 3 or 4 values (red, green, blue, optional alpha), got %d" % len(pixel))
    a = pixel[3] if len(pixel) == 4 else 1.0
    return (pixel[0], pixel[1], pixel[2], a)


class SYChannelSplit:
    DESCRIPTION = "Splits a picture into four masks: red, green, blue and alpha (transparency). Alpha is all ones if the picture has none."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "MASK", "MASK", "MASK")
    RETURN_NAMES = ("red", "green", "blue", "alpha")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to split. Outputs are red, green, blue and alpha masks."}),
            }
        }

    def run(self, image):
        import torch

        need_image(image)
        c = image.shape[-1]
        if c not in (3, 4):
            raise ValueError("the picture must have 3 or 4 channels, got %d" % c)
        r = image[..., 0].contiguous()
        g = image[..., 1].contiguous()
        b = image[..., 2].contiguous()
        a = image[..., 3].contiguous() if c == 4 else torch.ones_like(r)
        return (r, g, b, a)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ChannelSplit", SYChannelSplit)
NODE_DISPLAY_NAME_MAPPINGS["SYChannelSplit"] = "Channel Split SY"
