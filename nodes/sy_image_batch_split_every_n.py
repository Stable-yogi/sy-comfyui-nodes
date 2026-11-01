"""Image Batch Split Every N SY: cuts a batch into slices of N and outputs one slice."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
    from ._sy_videoframes import split_range
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape
    from _sy_videoframes import split_range


LAST_SLICE = ["keep", "pad", "drop"]


def plan_slice(total, part_size, part, wrap=False, last_slice="keep"):
    """Pure function. Returns (start, end, parts_total, pad, info).

    wrap False refuses a slice number that does not exist; True goes round (part 5 of 4 slices is slice 1).
    last_slice: keep = the short last slice stays short; pad = it is filled up to part_size by repeating its last
    picture (pad says how many); drop = a short last slice does not exist.
    """
    total, part_size, part = int(total), int(part_size), int(part)
    if last_slice not in LAST_SLICE:
        raise ValueError("last_slice must be one of: %s, got %r" % (", ".join(LAST_SLICE), last_slice))
    if total < 1:
        raise ValueError("the batch has no pictures")
    if part_size < 1:
        raise ValueError("part_size must be at least 1, got %d" % part_size)
    if part < 0:
        raise ValueError("part cannot be negative, got %d" % part)
    full, rest = divmod(total, part_size)
    parts_total = full + (1 if rest else 0)
    if last_slice == "drop" and rest:
        if full == 0:
            raise ValueError("the batch has %d pictures, fewer than part_size %d, so with last_slice drop no slice is left. Lower part_size or use keep." % (total, part_size))
        parts_total = full
    used = part
    if part >= parts_total:
        if not wrap:
            raise ValueError("part %d does not exist: %d pictures in slices of %d make %d slices (numbers 0 to %d). Lower part or turn wrap on."
                             % (part, total, part_size, parts_total, parts_total - 1))
        used = part % parts_total
    start = used * part_size
    end = min(start + part_size, total)
    pad = (part_size - (end - start)) if (last_slice == "pad" and end - start < part_size) else 0
    info = "Slice %d of %d (pictures %d to %d of %d)." % (used + 1, parts_total, start, end - 1, total)
    if used != part:
        info += " Part %d wrapped round to slice %d." % (part, used)
    if pad:
        info += " The last slice was short, so its last picture was repeated %d times to fill %d." % (pad, part_size)
    elif end - start < part_size:
        info += " This slice is shorter than part_size (%d of %d)." % (end - start, part_size)
    if last_slice == "drop" and rest:
        info += " The short last slice of %d pictures is dropped." % rest
    return start, end, parts_total, pad, info


class SYImageBatchSplitEveryN:
    DESCRIPTION = ("Cuts a batch into slices of N pictures and gives you slice number K. The last slice may be shorter. "
                   "Optional wrap goes round to slice 0 instead of failing when part is too big. Optional last_slice can pad "
                   "the short last slice (repeating its last picture) or drop it. An info line says which pictures you got.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("images", "parts_total", "count", "start_index", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The batch of pictures to cut."}),
                "part_size": ("INT", {"default": 16, "min": 1, "max": 100000, "tooltip": "How many pictures go in each slice."}),
                "part": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Which slice to output, counting from 0."}),
            },
            "optional": {
                "wrap": ("BOOLEAN", {"default": False, "tooltip": "On: a part number that is too big goes round to the start instead of failing."}),
                "last_slice": (LAST_SLICE, {"default": "keep", "tooltip": "keep leaves a short last slice short. pad fills it up. drop removes it."}),
            },
        }

    def run(self, images, part_size, part, wrap=False, last_slice="keep"):
        check_shape(images.shape)
        start, end, parts_total, pad, info = plan_slice(images.shape[0], part_size, part, wrap, last_slice)
        out = images[start:end]
        if pad:
            import torch
            out = torch.cat([out, out[-1:].expand(pad, -1, -1, -1)], dim=0)
        return (out, parts_total, out.shape[0], start, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageBatchSplitEveryN", SYImageBatchSplitEveryN)
NODE_DISPLAY_NAME_MAPPINGS["SYImageBatchSplitEveryN"] = "Image Batch Split Every N SY"
