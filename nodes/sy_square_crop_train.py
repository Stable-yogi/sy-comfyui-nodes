"""Crop Square Centre For Training SY: cuts the biggest centred square from each picture and resizes it."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

METHODS = ("area", "bicubic", "bilinear", "nearest")


def centre_square(width, height):
    """Pure function. Returns (left, top, side) of the biggest square centred in a width x height picture."""
    if width < 1 or height < 1:
        raise ValueError("picture size must be at least 1x1 (got %sx%s)" % (width, height))
    side = min(width, height)
    return (width - side) // 2, (height - side) // 2, side


def crop_resize(images, size, method):
    """images is a [B,H,W,C] tensor. Returns [B,size,size,C]. torch is imported here."""
    import torch
    import torch.nn.functional as F

    if method not in METHODS:
        raise ValueError("unknown method %r; use one of: %s" % (method, ", ".join(METHODS)))
    left, top, side = centre_square(images.shape[2], images.shape[1])
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
    DESCRIPTION = "Cuts the biggest square from the middle of each picture and resizes it to the size you give, ready for training."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The pictures to crop. Every picture in the batch is cropped the same way."}),
                "size": ("INT", {"default": 1024, "min": 8, "max": 8192, "step": 8, "tooltip": "Width and height of the finished square in pixels."}),
                "method": (list(METHODS), {"default": "area", "tooltip": "How to resize. Area is best for shrinking, bicubic for enlarging."}),
            }
        }

    def run(self, images, size, method):
        return (crop_resize(images, size, method),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SquareCropTrain", SYSquareCropTrain)
NODE_DISPLAY_NAME_MAPPINGS["SYSquareCropTrain"] = "Crop Square Centre For Training SY"
