"""Crop Square Centre For Training SY: cuts the biggest centred square from each picture and resizes it."""
try:
    from ._sy_common import category, register
    from ._sy_d3_info import need_nonempty, plural, size_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_d3_info import need_nonempty, plural, size_text

METHODS = ("area", "bicubic", "bilinear", "nearest")
ANCHORS = ("centre", "top_left", "top", "bottom", "left", "right")


def centre_square(width, height):
    """Pure function. Returns (left, top, side) of the biggest square centred in a width x height picture."""
    if width < 1 or height < 1:
        raise ValueError("picture size must be at least 1x1 (got %sx%s)" % (width, height))
    side = min(width, height)
    return (width - side) // 2, (height - side) // 2, side


def square_box(width, height, anchor="centre"):
    """Pure function. (left, top, side) of the biggest square. anchor says where it sits in the long direction:
    top / bottom for a portrait (keeps heads), left / right for a landscape. A side that is already square is not moved."""
    if anchor not in ANCHORS:
        raise ValueError("anchor must be one of: %s, got %r" % (", ".join(ANCHORS), anchor))
    left, top, side = centre_square(width, height)
    if anchor in ("top", "top_left") and height > width:
        top = 0
    elif anchor == "bottom" and height > width:
        top = height - side
    if anchor in ("left", "top_left") and width > height:
        left = 0
    elif anchor == "right" and width > height:
        left = width - side
    return left, top, side


def crop_info(width, height, size, method, anchor="centre", count=1):
    """Pure function. Plain sentence: the crop, the resize and a warning when the picture is enlarged a lot."""
    left, top, side = square_box(width, height, anchor)
    text = "%s of %s: cut a %dx%d square (x=%d, y=%d, anchor %s), resized to %dx%d with %s." % (
        plural(count, "picture").capitalize(), size_text(width, height), side, side, left, top, anchor, size, size, method)
    if side == size:
        text = text.replace(", resized to %dx%d with %s" % (size, size, method), ", already the right size, so not resized")
    if size > side * 1.5:
        text += " The square is enlarged x%.1f, which makes soft training pictures: use a smaller size or a bigger source." % (size / float(side))
    return text


def crop_resize(images, size, method, anchor="centre"):
    """images is a [B,H,W,C] tensor. Returns [B,size,size,C]. torch is imported here."""
    import torch
    import torch.nn.functional as F

    if method not in METHODS:
        raise ValueError("unknown method %r; use one of: %s" % (method, ", ".join(METHODS)))
    left, top, side = square_box(images.shape[2], images.shape[1], anchor)
    sq = images[:, top:top + side, left:left + side, :]
    if side == size:
        return sq
    x = sq.permute(0, 3, 1, 2)
    if method in ("bicubic", "bilinear"):
        x = F.interpolate(x, size=(size, size), mode=method, align_corners=False, antialias=side > size)
    else:
        x = F.interpolate(x, size=(size, size), mode=method)
    return x.permute(0, 2, 3, 1).clamp(0.0, 1.0).contiguous()


class SYSquareCropTrain:
    DESCRIPTION = "Cuts the biggest square from the middle of each picture and resizes it to the size you give, ready for training. Anchor picks which part of a long picture is kept (top keeps heads). The info output says the crop and warns when a small picture is enlarged a lot."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The pictures to crop. Every picture in the batch is cropped the same way."}),
                "size": ("INT", {"default": 1024, "min": 8, "max": 8192, "step": 8, "tooltip": "Width and height of the finished square in pixels."}),
                "method": (list(METHODS), {"default": "area", "tooltip": "How to resize. Area is best for shrinking, bicubic for enlarging."}),
            },
            "optional": {
                "anchor": (list(ANCHORS), {"default": "centre", "tooltip": "Which part is kept: top for portraits (heads), left/right for wide pictures, top_left for both."}),
            },
        }

    def run(self, images, size, method, anchor="centre"):
        need_nonempty(images.shape)
        out = crop_resize(images, size, method, anchor)
        return (out, crop_info(int(images.shape[2]), int(images.shape[1]), int(size), method, anchor, int(images.shape[0])))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SquareCropTrain", SYSquareCropTrain)
NODE_DISPLAY_NAME_MAPPINGS["SYSquareCropTrain"] = "Crop Square Centre For Training SY"
