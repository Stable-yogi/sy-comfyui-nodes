"""Mask From Box SY: makes a mask with a white rectangle on a black canvas."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
    from . import _sy_d2_common as d2
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm
    import _sy_d2_common as d2


ANCHORS = ("top-left", "centre")


def check_anchor(anchor):
    if anchor not in ANCHORS:
        raise ValueError("anchor must be one of: %s, got %r" % (", ".join(ANCHORS), anchor))


def top_left(x, y, w, h, anchor="top-left"):
    """Pure function. With the centre anchor, x and y are the middle of the box, so move to its top-left corner."""
    check_anchor(anchor)
    return (int(x), int(y)) if anchor == "top-left" else (int(x) - int(w) // 2, int(y) - int(h) // 2)


def box_mask(x, y, w, h, width, height, anchor="top-left", invert=False, feather=0):
    """Pure function. Returns a nested-list mask [height][width]. A box beyond the canvas is cut off.
    Optional: centre anchor, invert (everything except the box), feather (soft edge in pixels)."""
    if width < 1 or height < 1:
        raise ValueError("canvas width and height must be at least 1")
    if feather < 0 or feather > mm.MAX_RADIUS:
        raise ValueError("feather must be between 0 and %d" % mm.MAX_RADIUS)
    left, top = top_left(x, y, w, h, anchor)
    out = mm.box_mask_list(left, top, int(w), int(h), int(width), int(height))
    if feather:
        out = mm.blur_list(out, int(feather))
    if invert:
        out = [[1.0 - v for v in r] for r in out]
    return out


def box_report(x, y, w, h, width, height):
    """Pure function. Where the box sits: 'inside', 'cut off at the left and top', or 'completely outside' (empty mask)."""
    if w < 0 or h < 0:
        raise ValueError("box width and height cannot be negative")
    if w == 0 or h == 0:
        return "the box has no width or height, so the mask is empty"
    bx, by, bw, bh = mm.clamp_box(x, y, w, h, width, height)
    if bw == 0 or bh == 0:
        return "the box is completely outside the %s canvas, so the mask is empty" % d2.size_text(width, height)
    cut = []
    if x < 0:
        cut.append("left")
    if y < 0:
        cut.append("top")
    if x + w > width:
        cut.append("right")
    if y + h > height:
        cut.append("bottom")
    if not cut:
        return "the box %s at %d,%d is inside the canvas" % (d2.size_text(w, h), x, y)
    return "the box was cut off at the %s (%s of %s is inside)" % (" and ".join(cut), d2.size_text(bw, bh), d2.size_text(w, h))


class SYMaskFromBox:
    DESCRIPTION = ("Makes a mask that is white inside a rectangle and black elsewhere. Parts outside the canvas are cut off. "
                   "Connect a picture to copy its size, place the box by its centre, feather it or invert it. The info line tells if the box was cut off or missed the canvas.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "STRING")
    RETURN_NAMES = ("mask", "info")

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
            },
            "optional": {
                "size_from": ("IMAGE", {"tooltip": "Optional picture whose width and height are used as the canvas. Stops size mismatches."}),
                "anchor": (list(ANCHORS), {"default": "top-left", "tooltip": "top-left: x and y are the box corner. centre: x and y are the middle of the box."}),
                "feather": ("INT", {"default": 0, "min": 0, "max": mm.MAX_RADIUS, "step": 1, "tooltip": "Soften the box edge by this many pixels. 0 is a hard edge."}),
                "invert": ("BOOLEAN", {"default": False, "tooltip": "Swap white and black: everything except the box is selected."}),
            },
        }

    def run(self, x, y, box_width, box_height, canvas_width, canvas_height, size_from=None, anchor="top-left", feather=0, invert=False):
        import torch
        if size_from is not None:
            canvas_height, canvas_width = int(size_from.shape[1]), int(size_from.shape[2])
        check_anchor(anchor)
        if feather < 0 or feather > mm.MAX_RADIUS:
            raise ValueError("feather must be between 0 and %d" % mm.MAX_RADIUS)
        left, top = top_left(x, y, box_width, box_height, anchor)
        report = box_report(left, top, int(box_width), int(box_height), int(canvas_width), int(canvas_height))
        bx, by, bw, bh = mm.clamp_box(left, top, int(box_width), int(box_height), int(canvas_width), int(canvas_height))
        m = torch.zeros((1, int(canvas_height), int(canvas_width)), dtype=torch.float32)
        m[:, by:by + bh, bx:bx + bw] = 1.0
        if feather:
            m = mm.t_blur(m, int(feather))
        if invert:
            m = 1.0 - m
        info = "Mask %s: %s%s%s." % (d2.size_text(canvas_width, canvas_height), report,
                                      ", feathered %d px" % feather if feather else "", ", inverted" if invert else "")
        if size_from is not None:
            info += " Size taken from the connected picture."
        return (m, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskFromBox", SYMaskFromBox)
