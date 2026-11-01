"""Crop To Aspect SY: cuts the biggest area of a chosen shape (for example 16:9) out of a picture."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image


def crop_box(width, height, aspect_w, aspect_h, offset_x=0.0, offset_y=0.0):
    """Pure function. Returns (x, y, crop_w, crop_h). Offsets run -1 (left/top) to 1 (right/bottom), 0 is centre."""
    if min(width, height) < 1:
        raise ValueError("picture size must be at least 1x1")
    if aspect_w < 1 or aspect_h < 1:
        raise ValueError("aspect numbers must be at least 1, got %s:%s" % (aspect_w, aspect_h))
    ox = max(-1.0, min(1.0, float(offset_x)))
    oy = max(-1.0, min(1.0, float(offset_y)))
    if width * aspect_h >= height * aspect_w:  # picture is wider than wanted: cut the sides
        ch = height
        cw = max(1, min(width, int(round(height * aspect_w / float(aspect_h)))))
    else:
        cw = width
        ch = max(1, min(height, int(round(width * aspect_h / float(aspect_w)))))
    x = int(round((width - cw) * (ox + 1.0) / 2.0))
    y = int(round((height - ch) * (oy + 1.0) / 2.0))
    return (x, y, cw, ch)


def snap_size(cw, ch, multiple_of):
    """Pure function. Shrinks the crop to a multiple of `multiple_of` (never below one step, never above the crop)."""
    if multiple_of < 1:
        raise ValueError("multiple_of must be 1 or more, got %s" % multiple_of)
    if multiple_of == 1:
        return cw, ch
    return max(1, min(cw, cw // multiple_of * multiple_of or cw)), max(1, min(ch, ch // multiple_of * multiple_of or ch))


def crop_info(width, height, x, y, cw, ch):
    """Pure function. One plain sentence."""
    return "Cropped %dx%d -> %dx%d (took x=%d, y=%d)" % (width, height, cw, ch, x, y)


class SYCropToAspect:
    DESCRIPTION = "Crops a picture to a shape such as 16:9 or 1:1. Takes the biggest area of that shape, centred or moved with the offsets. Can snap the size to a multiple of 8 or 64 and says what it took."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT", "STRING")
    RETURN_NAMES = ("image", "width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to crop."}),
                "aspect_w": ("INT", {"default": 16, "min": 1, "max": 1000, "tooltip": "Width part of the shape, the 16 in 16:9."}),
                "aspect_h": ("INT", {"default": 9, "min": 1, "max": 1000, "tooltip": "Height part of the shape, the 9 in 16:9."}),
                "offset_x": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Moves the crop sideways. -1 is left, 0 is centre, 1 is right."}),
                "offset_y": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Moves the crop up or down. -1 is top, 0 is centre, 1 is bottom."}),
            },
            "optional": {
                "multiple_of": ("INT", {"default": 1, "min": 1, "max": 512, "step": 1, "tooltip": "Trim the crop so width and height are multiples of this, for example 8 or 64. 1 = off."}),
            },
        }

    def run(self, image, aspect_w, aspect_h, offset_x, offset_y, multiple_of=1):
        need_image(image)
        x, y, cw, ch = crop_box(image.shape[2], image.shape[1], aspect_w, aspect_h, offset_x, offset_y)
        if multiple_of > 1:
            cw, ch = snap_size(cw, ch, multiple_of)
            x = min(x, image.shape[2] - cw)
            y = min(y, image.shape[1] - ch)
        return (image[:, y:y + ch, x:x + cw, :].contiguous(), cw, ch, crop_info(image.shape[2], image.shape[1], x, y, cw, ch))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CropToAspect", SYCropToAspect)
NODE_DISPLAY_NAME_MAPPINGS["SYCropToAspect"] = "Crop To Aspect SY"
