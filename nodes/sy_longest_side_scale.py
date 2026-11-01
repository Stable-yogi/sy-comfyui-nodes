"""Longest Side Scale SY: scale a size so its longest side hits a target, keeping the aspect."""
try:
    from ._sy_common import category, register
    from ._sy_b_sizeinfo import size_facts
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_b_sizeinfo import size_facts

MAX_SIDE = 65536


def _round_to(value, multiple):
    """Round to the nearest multiple (halves go up), never below one multiple."""
    return max(multiple, int(value / multiple + 0.5) * multiple)


def scale_longest_side(width, height, longest_side, multiple, no_upscale=False, max_megapixels=0.0):
    """Pure function. Returns (w, h). The longer side becomes `longest_side` (rounded to `multiple`).
    no_upscale never makes the picture bigger. max_megapixels above 0 is a memory-safety cap."""
    width, height, longest_side, multiple = int(width), int(height), int(longest_side), int(multiple)
    max_megapixels = float(max_megapixels)
    if not max_megapixels >= 0:
        raise ValueError("max_megapixels must be 0 (off) or more, got %s" % max_megapixels)
    if width < 1 or height < 1:
        raise ValueError("width and height must be at least 1, got %dx%d" % (width, height))
    if longest_side < 1 or longest_side > MAX_SIDE:
        raise ValueError("longest_side must be between 1 and %d, got %d" % (MAX_SIDE, longest_side))
    if multiple < 1:
        raise ValueError("multiple must be at least 1, got %d" % multiple)
    if no_upscale:
        longest_side = min(longest_side, max(width, height))
    long_out = _round_to(longest_side, multiple)

    def build(long_side):
        if width >= height:
            return long_side, _round_to(long_side * height / width, multiple)
        return _round_to(long_side * width / height, multiple), long_side

    w, h = build(long_out)
    if max_megapixels > 0:
        cap = max_megapixels * 1_000_000
        if multiple * multiple > cap:
            raise ValueError("max_megapixels %g is too small: even %dx%d is over it. Raise it or lower multiple." % (max_megapixels, multiple, multiple))
        while w * h > cap and long_out > multiple:
            long_out -= multiple
            w, h = build(long_out)
    return (w, h)


def scale_report(width, height, longest_side, multiple, no_upscale=False, max_megapixels=0.0):
    """Pure function. Returns (w, h, info)."""
    w, h = scale_longest_side(width, height, longest_side, multiple, no_upscale, max_megapixels)
    width, height = int(width), int(height)
    info = "%dx%d -> %dx%d (x%.3g, %s)" % (width, height, w, h, max(w, h) / float(max(width, height)), size_facts(w, h))
    plain = scale_longest_side(width, height, longest_side, multiple)
    if (w, h) != plain:
        info += ", limited by %s" % ("no_upscale" if no_upscale and max(plain) > max(width, height) and (w, h) == scale_longest_side(width, height, longest_side, multiple, True) else "the megapixel cap")
    return w, h, info


class SYLongestSideScale:
    DESCRIPTION = "Works out a new width and height so the longer side equals the number you give. The shape (aspect) stays the same. Both sides are rounded to a multiple. Optional no_upscale and a megapixel cap keep small pictures small and big ones safe. The info line explains the result."
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Current width in pixels."}),
                "height": ("INT", {"default": 768, "min": 1, "max": MAX_SIDE, "tooltip": "Current height in pixels."}),
                "longest_side": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Size in pixels you want for the longer side."}),
                "multiple": ("INT", {"default": 8, "min": 1, "max": 256, "tooltip": "Both sides are rounded to a multiple of this. Use 1 for exact."}),
            },
            "optional": {
                "no_upscale": ("BOOLEAN", {"default": False, "tooltip": "On never makes the picture bigger than it is now. Small pictures keep their size."}),
                "max_megapixels": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 4096.0, "step": 0.1, "tooltip": "0 is off. Example: 2.0 keeps the result under 2 million pixels so it fits your card."}),
            },
        }

    def run(self, width, height, longest_side, multiple, no_upscale=False, max_megapixels=0.0):
        return scale_report(width, height, longest_side, multiple, bool(no_upscale), max_megapixels)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LongestSideScale", SYLongestSideScale)
NODE_DISPLAY_NAME_MAPPINGS["SYLongestSideScale"] = "Longest Side Scale SY"
