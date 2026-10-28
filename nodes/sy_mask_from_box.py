"""Mask From Box SY: makes a mask with a white rectangle on a black canvas."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm


def box_mask(x, y, w, h, width, height):
    """Pure function. Returns a nested-list mask [height][width]. A box beyond the canvas is cut off."""
    if width < 1 or height < 1:
        raise ValueError("canvas width and height must be at least 1")
    return mm.box_mask_list(int(x), int(y), int(w), int(h), int(width), int(height))


class SYMaskFromBox:
    DESCRIPTION = "Makes a mask that is white inside a rectangle and black elsewhere. Parts outside the canvas are cut off."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        big = 16384
        return {
            "required": {
                "x": ("INT", {"default": 0, "min": -big, "max": big, "step": 1, "tooltip": "Left edge of the box in pixels."}),
                "y": ("INT", {"default": 0, "min": -big, "max": big, "step": 1, "tooltip": "Top edge of the box in pixels."}),
                "box_width": ("INT", {"default": 256, "min": 0, "max": big, "step": 1, "tooltip": "Width of the box in pixels."}),
                "box_height": ("INT", {"default": 256, "min": 0, "max": big, "step": 1, "tooltip": "Height of the box in pixels."}),
                "canvas_width": ("INT", {"default": 1024, "min": 1, "max": big, "step": 1, "tooltip": "Width of the mask in pixels."}),
                "canvas_height": ("INT", {"default": 1024, "min": 1, "max": big, "step": 1, "tooltip": "Height of the mask in pixels."}),
            }
        }

    def run(self, x, y, box_width, box_height, canvas_width, canvas_height):
        import torch
        bx, by, bw, bh = mm.clamp_box(int(x), int(y), int(box_width), int(box_height), int(canvas_width), int(canvas_height))
        m = torch.zeros((1, int(canvas_height), int(canvas_width)), dtype=torch.float32)
        m[:, by:by + bh, bx:bx + bw] = 1.0
        return (m,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskFromBox", SYMaskFromBox)
