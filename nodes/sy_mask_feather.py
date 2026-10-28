"""Mask Feather SY: softens the edge of a mask."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm


def feather(rows, radius):
    """Pure function on a nested-list mask [H][W]."""
    if radius < 0 or radius > mm.MAX_RADIUS:
        raise ValueError("radius must be between 0 and %d" % mm.MAX_RADIUS)
    return mm.blur_list(rows, int(radius))


class SYMaskFeather:
    DESCRIPTION = "Softens the edge of a mask with a smooth blur so it blends in. Radius 0 changes nothing."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", {"tooltip": "The mask to soften."}),
                "radius": ("INT", {"default": 16, "min": 0, "max": mm.MAX_RADIUS, "step": 1, "tooltip": "How many pixels wide the soft edge is. 0 keeps the mask as it is."}),
            }
        }

    def run(self, mask, radius):
        if radius < 0 or radius > mm.MAX_RADIUS:
            raise ValueError("radius must be between 0 and %d" % mm.MAX_RADIUS)
        return (mm.t_blur(mm.t_mask3(mask), int(radius)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskFeather", SYMaskFeather)
