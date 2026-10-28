"""Mask To Box SY: finds the rectangle around the white part of a mask."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm

EMPTY_CHOICES = ("whole_image", "error")


def _finish(box, padding, on_empty, w, h):
    if box is None:
        if on_empty == "error":
            raise ValueError("the mask is empty: paint something white, or set on_empty to whole_image")
        return (0, 0, w, h)
    return mm.pad_box(box, padding, w, h)


def mask_to_box(rows, padding, threshold, on_empty):
    """Pure function on a nested-list mask [H][W]. Returns (x, y, w, h), padded and kept inside the image."""
    if padding < 0:
        raise ValueError("padding cannot be negative")
    if on_empty not in EMPTY_CHOICES:
        raise ValueError("on_empty must be whole_image or error")
    return _finish(mm.mask_bbox(rows, threshold), padding, on_empty, len(rows[0]), len(rows))


class SYMaskToBox:
    DESCRIPTION = "Finds the rectangle around the white part of a mask and returns x, y, width, height, with optional padding."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "INT", "INT")
    RETURN_NAMES = ("x", "y", "width", "height")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", {"tooltip": "The mask to measure. A batch gives one box around all of them."}),
                "padding": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 1, "tooltip": "Extra pixels added around the box. The box stays inside the image."}),
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.01, "max": 1.0, "step": 0.01, "tooltip": "Mask values at or above this count as white."}),
                "on_empty": (list(EMPTY_CHOICES), {"default": "whole_image", "tooltip": "When nothing is white: use the whole image, or stop with an error."}),
            }
        }

    def run(self, mask, padding, threshold, on_empty):
        if padding < 0:
            raise ValueError("padding cannot be negative")
        if on_empty not in EMPTY_CHOICES:
            raise ValueError("on_empty must be whole_image or error")
        m = mm.t_mask3(mask)
        return _finish(mm.t_bbox(m, threshold), int(padding), on_empty, m.shape[2], m.shape[1])


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskToBox", SYMaskToBox)
