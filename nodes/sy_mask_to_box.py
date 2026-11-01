"""Mask To Box SY: finds the rectangle around the white part of a mask."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
    from ._sy_d3_info import pct_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm
    from _sy_d3_info import pct_text

EMPTY_CHOICES = ("whole_image", "error")


def _finish(box, padding, on_empty, w, h):
    if box is None:
        if on_empty == "error":
            raise ValueError("the mask is empty: paint something white, or set on_empty to whole_image")
        return (0, 0, w, h)
    return mm.pad_box(box, padding, w, h)


def finish_box(box, padding, on_empty, w, h, multiple_of=1):
    """Pure function. Like _finish but also snaps the size up to a multiple (when the mask is not empty).
    Returns (x, y, width, height, was_empty)."""
    if multiple_of < 1:
        raise ValueError("multiple_of must be 1 or more, got %s" % multiple_of)
    out = _finish(box, padding, on_empty, w, h)
    if box is None:
        return out + (True,)
    if multiple_of > 1:
        out = mm.fit_multiple(out, int(multiple_of), w, h)
    return tuple(out) + (False,)


def box_info(x, y, bw, bh, img_w, img_h, was_empty, padding=0, multiple_of=1):
    """Pure function. Plain sentence describing the box."""
    if was_empty:
        return "The mask is empty (nothing at or above the threshold), so the whole %dx%d image is used as the box." % (img_w, img_h)
    text = "Box at x=%d, y=%d, size %dx%d (%s of the %dx%d image)" % (x, y, bw, bh, pct_text(bw * bh, img_w * img_h), img_w, img_h)
    extra = []
    if padding:
        extra.append("padding %d" % padding)
    if multiple_of > 1:
        extra.append("size snapped to a multiple of %d" % multiple_of)
    if extra:
        text += ", " + ", ".join(extra)
    return text + "."


def mask_to_box(rows, padding, threshold, on_empty):
    """Pure function on a nested-list mask [H][W]. Returns (x, y, w, h), padded and kept inside the image."""
    if padding < 0:
        raise ValueError("padding cannot be negative")
    if on_empty not in EMPTY_CHOICES:
        raise ValueError("on_empty must be whole_image or error")
    return _finish(mm.mask_bbox(rows, threshold), padding, on_empty, len(rows[0]), len(rows))


class SYMaskToBox:
    DESCRIPTION = "Finds the rectangle around the white part of a mask and returns x, y, width, height, with optional padding and an option to make the size a multiple of 8, 16 or 64 for samplers. The info output explains the box and warns when the mask is empty."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("x", "y", "width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", {"tooltip": "The mask to measure. A batch gives one box around all of them."}),
                "padding": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 1, "tooltip": "Extra pixels added around the box. The box stays inside the image."}),
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.01, "max": 1.0, "step": 0.01, "tooltip": "Mask values at or above this count as white."}),
                "on_empty": (list(EMPTY_CHOICES), {"default": "whole_image", "tooltip": "When nothing is white: use the whole image, or stop with an error."}),
            },
            "optional": {
                "multiple_of": ("INT", {"default": 1, "min": 1, "max": 512, "step": 1, "tooltip": "Grow the box so width and height are multiples of this, for example 8 or 64. 1 keeps the exact box."}),
            },
        }

    def run(self, mask, padding, threshold, on_empty, multiple_of=1):
        if padding < 0:
            raise ValueError("padding cannot be negative")
        if on_empty not in EMPTY_CHOICES:
            raise ValueError("on_empty must be whole_image or error")
        m = mm.t_mask3(mask)
        if m.shape[0] < 1:
            raise ValueError("the mask batch is empty: connect at least 1 mask")
        iw, ih = int(m.shape[2]), int(m.shape[1])
        x, y, bw, bh, was_empty = finish_box(mm.t_bbox(m, threshold), int(padding), on_empty, iw, ih, int(multiple_of))
        return (x, y, bw, bh, box_info(x, y, bw, bh, iw, ih, was_empty, int(padding), int(multiple_of)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskToBox", SYMaskToBox)
