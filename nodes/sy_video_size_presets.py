"""Video Size Presets SY: video sizes at 480p, 720p and 1080p in 16:9, 9:16 and 1:1."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

RESOLUTIONS = {"480p": 480, "720p": 720, "1080p": 1080}
ASPECTS = {"16:9": (16, 9), "9:16": (9, 16), "1:1": (1, 1)}
MULTIPLES = (16, 32)


def _round_to(value, multiple):
    return max(multiple, int(value / multiple + 0.5) * multiple)


def video_size(resolution, aspect, multiple):
    """Pure function. Returns (w, h). The short side is the p-number, both sides are multiples."""
    if resolution not in RESOLUTIONS:
        raise ValueError("unknown resolution %r, pick one of: %s" % (resolution, ", ".join(RESOLUTIONS)))
    if aspect not in ASPECTS:
        raise ValueError("unknown aspect %r, pick one of: %s" % (aspect, ", ".join(ASPECTS)))
    multiple = int(multiple)
    if multiple not in MULTIPLES:
        raise ValueError("multiple must be 16 or 32, got %d" % multiple)
    short = RESOLUTIONS[resolution]
    aw, ah = ASPECTS[aspect]
    if aw >= ah:
        w, h = short * aw / ah, short
    else:
        w, h = short, short * ah / aw
    return (_round_to(w, multiple), _round_to(h, multiple))


class SYVideoSizePresets:
    DESCRIPTION = ("Video sizes for models like Wan and LTX. Pick 480p, 720p or 1080p and a shape: "
                   "wide 16:9, tall 9:16 or square 1:1. Both sides are rounded to 16 or 32.")
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "resolution": (list(RESOLUTIONS), {"default": "720p", "tooltip": "Length of the short side. 720p is 720 pixels."}),
                "aspect": (list(ASPECTS), {"default": "16:9", "tooltip": "16:9 is wide, 9:16 is tall like a phone, 1:1 is square."}),
                "multiple": ([str(m) for m in MULTIPLES], {"default": "16", "tooltip": "Round both sides to this multiple. LTX style models like 32."}),
            }
        }

    def run(self, resolution, aspect, multiple):
        return video_size(resolution, aspect, int(multiple))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VideoSizePresets", SYVideoSizePresets)
NODE_DISPLAY_NAME_MAPPINGS["SYVideoSizePresets"] = "Video Size Presets SY"
