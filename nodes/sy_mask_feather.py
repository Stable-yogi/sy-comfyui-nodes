"""Mask Feather SY: softens the edge of a mask."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
    from . import _sy_d2_common as d2
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm
    import _sy_d2_common as d2


EDGES = ("centred", "inside only", "outside only")


def check_edge(edge):
    if edge not in EDGES:
        raise ValueError("edge must be one of: %s, got %r" % (", ".join(EDGES), edge))


def feather(rows, radius, edge="centred", grow=0):
    """Pure function on a nested-list mask [H][W].
    grow (pixels, negative shrinks) happens first, then the blur. edge: centred = the soft edge straddles the old edge;
    inside only = the mask never gets bigger than before the blur (no halo outside); outside only = never smaller."""
    if radius < 0 or radius > mm.MAX_RADIUS:
        raise ValueError("radius must be between 0 and %d" % mm.MAX_RADIUS)
    if abs(grow) > mm.MAX_RADIUS:
        raise ValueError("grow must be between -%d and %d pixels, got %s" % (mm.MAX_RADIUS, mm.MAX_RADIUS, grow))
    check_edge(edge)
    base = mm.grow_shrink_list(rows, int(grow)) if grow else [list(r) for r in rows]
    blurred = mm.blur_list(base, int(radius))
    if edge == "centred" or radius == 0:
        return blurred
    pick = min if edge == "inside only" else max
    return [[pick(u, v) for u, v in zip(rb, rr)] for rb, rr in zip(blurred, base)]


def feather_info(radius, edge, grow, width, height, pct_before, pct_after):
    """Pure function. One plain line: what was done and how much the mask covers before and after."""
    if radius == 0 and not grow:
        return "Radius 0 and no grow: the mask was left as it is (%s)." % d2.coverage_text(pct_before)
    steps = []
    if grow:
        steps.append("%s %d px" % ("grown" if grow > 0 else "shrunk", abs(grow)))
    if radius:
        steps.append("feathered %d px (%s)" % (radius, edge))
    text = "Mask %s, in this order; %s -> %s." % (", then ".join(steps), d2.coverage_text(pct_before), d2.coverage_text(pct_after))
    if pct_before <= 0.0:
        text += " The input mask is empty, so there is nothing to feather."
    if radius * 2 > min(width, height):
        text += " The radius is more than half the picture; the soft edge covers most of it."
    return text


class SYMaskFeather:
    DESCRIPTION = ("Softens the edge of a mask with a smooth blur so it blends in. Radius 0 changes nothing. Can grow first and "
                   "then feather (the right order), and keep the soft edge inside the old edge so no halo appears outside the subject.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "STRING")
    RETURN_NAMES = ("mask", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", {"tooltip": "The mask to soften."}),
                "radius": ("INT", {"default": 16, "min": 0, "max": mm.MAX_RADIUS, "step": 1, "tooltip": "How many pixels wide the soft edge is. 0 keeps the mask as it is."}),
            },
            "optional": {
                "grow": ("INT", {"default": 0, "min": -mm.MAX_RADIUS, "max": mm.MAX_RADIUS, "step": 1, "tooltip": "Grow the white area by this many pixels BEFORE feathering (negative shrinks). 0 is off."}),
                "edge": (list(EDGES), {"default": "centred", "tooltip": "centred: soft edge on both sides. inside only: no halo outside. outside only: no shrinking."}),
            },
        }

    def run(self, mask, radius, grow=0, edge="centred"):
        if radius < 0 or radius > mm.MAX_RADIUS:
            raise ValueError("radius must be between 0 and %d" % mm.MAX_RADIUS)
        if abs(grow) > mm.MAX_RADIUS:
            raise ValueError("grow must be between -%d and %d pixels, got %s" % (mm.MAX_RADIUS, mm.MAX_RADIUS, grow))
        check_edge(edge)
        m = mm.t_mask3(mask)
        base = mm.t_grow_shrink(m, int(grow)) if grow else m
        out = mm.t_blur(base, int(radius))
        if radius and edge != "centred":
            import torch
            out = torch.minimum(out, base) if edge == "inside only" else torch.maximum(out, base)
        info = feather_info(int(radius), edge, int(grow), m.shape[2], m.shape[1], 100.0 * float(m.mean()), 100.0 * float(out.mean()))
        return (out.contiguous(), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskFeather", SYMaskFeather)
