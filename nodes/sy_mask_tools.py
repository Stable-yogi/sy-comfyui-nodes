"""Mask Tools SY: clean up a mask in one node (threshold, grow or shrink, feather, invert) and see the result on the picture."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
    from . import _sy_d2_common as d2
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm
    import _sy_d2_common as d2

EDGES = ("centred", "inside only", "outside only")
OVERLAY_COLOURS = {"red": (1.0, 0.0, 0.0), "green": (0.0, 1.0, 0.0), "blue": (0.0, 0.4, 1.0), "yellow": (1.0, 0.9, 0.0),
                   "magenta": (1.0, 0.0, 1.0), "cyan": (0.0, 1.0, 1.0)}


def check_settings(threshold, grow, feather, edge, overlay_colour, overlay_opacity):
    """Pure function. Plain refusals before any work starts."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1 (0 = off), got %s" % threshold)
    if abs(grow) > mm.MAX_RADIUS:
        raise ValueError("grow must be between -%d and %d pixels, got %s" % (mm.MAX_RADIUS, mm.MAX_RADIUS, grow))
    if feather < 0 or feather > mm.MAX_RADIUS:
        raise ValueError("feather must be between 0 and %d pixels, got %s" % (mm.MAX_RADIUS, feather))
    if edge not in EDGES:
        raise ValueError("edge must be one of: %s, got %r" % (", ".join(EDGES), edge))
    if overlay_colour not in OVERLAY_COLOURS:
        raise ValueError("overlay_colour must be one of: %s, got %r" % (", ".join(OVERLAY_COLOURS), overlay_colour))
    if not 0.0 <= overlay_opacity <= 1.0:
        raise ValueError("overlay_opacity must be between 0 and 1, got %s" % overlay_opacity)


def process(rows, threshold=0.0, grow=0, feather=0, edge="centred", invert=False, invert_first=False):
    """Pure function on a nested-list mask [H][W]. Order: invert first (only when asked), threshold, grow or shrink,
    feather, invert last. Feather happens after grow, so the soft edge sits on the new edge."""
    check_settings(threshold, grow, feather, edge, "red", 0.5)
    m = [list(r) for r in rows]
    if invert_first:
        m = mm.threshold_invert_list(m, True, False, 0.0)
    if threshold > 0.0:
        m = mm.threshold_invert_list(m, False, True, threshold)
    if grow:
        m = mm.grow_shrink_list(m, int(grow))
    if feather:
        base = m
        m = mm.blur_list(base, int(feather))
        if edge != "centred":
            pick = min if edge == "inside only" else max
            m = [[pick(u, v) for u, v in zip(rb, rr)] for rb, rr in zip(m, base)]
    if invert and not invert_first:
        m = mm.threshold_invert_list(m, True, False, 0.0)
    return m


def coverage(rows):
    """Pure function. Percent of the mask that is white (mean value)."""
    total = sum(len(r) for r in rows)
    return d2.coverage_percent(total, sum(sum(r) for r in rows))


def tools_info(threshold, grow, feather, edge, invert, invert_first, pct_before, pct_after, stretched=""):
    """Pure function. One plain line: the steps in the order they ran, and the coverage before and after."""
    steps = []
    if invert_first:
        steps.append("inverted first")
    if threshold > 0.0:
        steps.append("hardened at %g" % threshold)
    if grow:
        steps.append("%s %d px" % ("grown" if grow > 0 else "shrunk", abs(grow)))
    if feather:
        steps.append("feathered %d px (%s)" % (feather, edge))
    if invert and not invert_first:
        steps.append("inverted")
    if not steps:
        return d2.join_info(["Mask Tools: all settings are neutral, the mask was left as it is (%s)" % d2.coverage_text(pct_before), stretched])
    text = "Mask Tools: " + ", then ".join(steps) + "; " + d2.coverage_text(pct_before) + " -> " + d2.coverage_text(pct_after)
    if pct_before <= 0.0 and not (invert or invert_first):
        text += ". The input mask is empty, so there is nothing to work on"
    return d2.join_info([text, stretched])


def _process_tensor(mask, threshold, grow, feather, edge, invert, invert_first):
    m = mask
    if invert_first:
        m = 1.0 - m
    if threshold > 0.0:
        m = (m >= threshold).to(m.dtype)
    if grow:
        m = mm.t_grow_shrink(m, int(grow))
    if feather:
        base = m
        m = mm.t_blur(base, int(feather))
        if edge == "inside only":
            m = m.minimum(base)
        elif edge == "outside only":
            m = m.maximum(base)
    if invert and not invert_first:
        m = 1.0 - m
    return m.clamp(0.0, 1.0)


def _overlay(image, mask, colour, opacity):
    """Picture with the mask tinted on top. No picture: the mask as a grey picture."""
    import torch
    if image is None:
        return mask.unsqueeze(-1).repeat(1, 1, 1, 3).contiguous()
    rgb = image[..., :3]
    tint = torch.tensor(OVERLAY_COLOURS[colour], dtype=rgb.dtype, device=rgb.device)
    w = (mask.unsqueeze(-1).to(rgb.device, rgb.dtype) * opacity)
    return (rgb + (tint - rgb) * w).clamp(0.0, 1.0).contiguous()


class SYMaskTools:
    DESCRIPTION = ("Cleans up a mask in one node: make it hard (threshold), grow or shrink it, feather the edge, invert it, in the "
                   "right order. Connect the picture to see the mask tinted on it. The info line says what was done and how much "
                   "of the picture the mask covers before and after. All settings start neutral.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "IMAGE", "STRING")
    RETURN_NAMES = ("mask", "preview", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", {"tooltip": "The mask to clean up."}),
            },
            "optional": {
                "threshold": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Makes the mask hard black and white at this level. 0 = off, 0.5 is typical."}),
                "grow": ("INT", {"default": 0, "min": -512, "max": 512, "tooltip": "Pixels to grow (above 0) or shrink (below 0) the white area. Try 8."}),
                "feather": ("INT", {"default": 0, "min": 0, "max": 512, "tooltip": "Soft edge in pixels, applied after grow. Try 12."}),
                "edge": (list(EDGES), {"default": "centred", "tooltip": "centred = soft edge straddles the old edge. inside only = no halo outside the subject."}),
                "invert": ("BOOLEAN", {"default": False, "tooltip": "Flip white and black after all other steps."}),
                "invert_first": ("BOOLEAN", {"default": False, "tooltip": "Flip white and black before the other steps instead of after."}),
                "image": ("IMAGE", {"tooltip": "Optional. The preview shows the mask tinted on this picture, and the mask is stretched to its size."}),
                "overlay_colour": (list(OVERLAY_COLOURS), {"default": "red", "tooltip": "Tint colour for the preview."}),
                "overlay_opacity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05, "tooltip": "How strong the tint is in the preview. 0.5 is half."}),
            },
        }

    def run(self, mask, threshold=0.0, grow=0, feather=0, edge="centred", invert=False, invert_first=False, image=None,
            overlay_colour="red", overlay_opacity=0.5):
        check_settings(threshold, grow, feather, edge, overlay_colour, overlay_opacity)
        d2.shape_of_mask(tuple(mask.shape))
        m = mm.t_mask3(mask)
        stretched = ""
        if image is not None:
            if getattr(image, "ndim", 0) != 4 or image.shape[3] < 3:
                raise ValueError("the picture must be a colour picture shaped [batch, height, width, channels]")
            h, w = image.shape[1], image.shape[2]
            stretched = d2.mask_note(tuple(mask.shape), h, w)
            m = d2.t_mask_for_image(mask, image.shape[0], h, w).squeeze(-1)
        before = 100.0 * float(m.mean())
        out = _process_tensor(m, threshold, grow, feather, edge, invert, invert_first)
        after = 100.0 * float(out.mean())
        info = tools_info(threshold, grow, feather, edge, invert, invert_first, before, after, stretched)
        prev_mask = out
        if image is not None and image.shape[0] != out.shape[0]:
            prev_mask = mm.t_match_batch(out, image.shape[0])
        return (out, _overlay(image, prev_mask, overlay_colour, overlay_opacity), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskTools", SYMaskTools)
NODE_DISPLAY_NAME_MAPPINGS["SYMaskTools"] = "Mask Tools SY"
